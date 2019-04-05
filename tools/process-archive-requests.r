processArchiveRequest() {
	# Scan for published vault packages that require archiving.
	*ContInxOld = 1;
	msiAddSelectFieldToGenQuery("COLL_NAME", "", *GenQ2Inp);
	msiAddConditionToGenQuery("COLL_NAME", "like", "%%/home/vault-%%", *GenQ2Inp);
	msiAddConditionToGenQuery("META_COLL_ATTR_NAME", "=", UUORGMETADATAPREFIX ++ "vault_status", *GenQ2Inp);
	msiAddConditionToGenQuery("META_COLL_ATTR_VALUE", "=", ARCHIVE_REQUEST, *GenQ2Inp);

	msiExecGenQuery(*GenQ2Inp, *GenQ2Out);
	msiGetContInxFromGenQueryOut(*GenQ2Out, *ContInxNew);

	while(*ContInxOld > 0) {
		foreach(*row in *GenQ2Out) {
			*collName = *row.COLL_NAME;

			# Check if this really is a vault package
			if (*collName like regex "/[^/]+/home/vault-.*") {
				*err = errorcode(iiProcessArchiveRequest(*collName, *status));
				if (*err < 0) {
					writeLine("stdout", "iiProcessArchiveRequest *collName returned errorcode *err");
				} else {
					writeLine("stdout", "iiProcessArchiveRequest *collName returned with status: *status");
				}
				writeLine('stdout', *collName);
			}
		}

		*ContInxOld = *ContInxNew;
		if(*ContInxOld > 0) {
			msiGetMoreRows(*GenQ2Inp, *GenQ2Out, *ContInxNew);
		}
	}
	msiCloseGenQuery(*GenQ2Inp, *GenQ2Out);
}
input null
output ruleExecOut
