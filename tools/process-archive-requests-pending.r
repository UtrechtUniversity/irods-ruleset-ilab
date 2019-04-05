processArchiveRequestPending() {
	# Scan for vault packages which are being archived which are being archived.   
	*ContInxOld = 1;
	msiAddSelectFieldToGenQuery("COLL_NAME", "", *GenQ3Inp);
	msiAddConditionToGenQuery("COLL_NAME", "like", "%%/home/vault-%%", *GenQ3Inp);
	msiAddConditionToGenQuery("META_COLL_ATTR_NAME", "=", UUORGMETADATAPREFIX ++ "vault_status", *GenQ3Inp);
	msiAddConditionToGenQuery("META_COLL_ATTR_VALUE", "=", PENDING_ARCHIVE_REQUEST, *GenQ3Inp);

	msiExecGenQuery(*GenQ3Inp, *GenQ3Out);
	msiGetContInxFromGenQueryOut(*GenQ3Out, *ContInxNew);

	while(*ContInxOld > 0) {
		foreach(*row in *GenQ3Out) {
			*collName = *row.COLL_NAME;

			# Check if this really is a vault package
			if (*collName like regex "/[^/]+/home/vault-.*") {
				*err = errorcode(iiProcessArchiveRequestPending(*collName, *status));
				if (*err < 0) {
					writeLine("stdout", "iiProcessArchiveRequestPending *collName returned errorcode *err");
				} else {
					writeLine("stdout", "iiProcessArchiveRequestPending *collName returned with status: *status");
				}
				writeLine('stdout', *collName);
			}
		}

		*ContInxOld = *ContInxNew;
		if(*ContInxOld > 0) {
			msiGetMoreRows(*GenQ3Inp, *GenQ3Out, *ContInxNew);
		}
	}
	msiCloseGenQuery(*GenQ3Inp, *GenQ3Out);
}
input null
output ruleExecOut
