# \file iiVault.r
# \brief Copy folders to the vault
#
# \author Paul Frederiks
# \copyright Copyright (c) 2016, Utrecht university. All rights reserved
# \license GPLv3, see LICENSE


# \brief iiCopyFolderToVault
# \param[in] folder  The folder to copy to the vault
iiCopyFolderToVault(*folder) {
	*err = errorcode(iiCollectionGroupName(*folder, *groupName));
	writeLine("stdout", "*folder - *groupName");
	if (*err < 0) {
		failmsg(-1, "NoResearchGroup");
	}
	uuChop(*groupName, *_, *baseName, "-", true);
	uuChopPath(*folder, *parent, *datapackageName);
	msiGetIcatTime(*timestamp, "unix");
        *vaultGroupName = "vault-*baseName";
	*target = "/$rodsZoneClient/home/*vaultGroupName/*datapackageName" ++ "_*timestamp";
	*buffer.source = *folder;
	*buffer.destination = *target;
	uuTreeWalk("forward", *folder, "iiIngestObject", *buffer, *error);
	iiCopyUserMetadata(*folder, *target);
	iiFolderSecure(*folder);
	iiCopyActionLog(*folder, *target);
}

# \brief iiIngestObject
# \param[in] itemParent
# \param[in] itemName
# \param[in] itemIsCollection
# \param[in/out] buffer
# \param[in/out] error
iiIngestObject(*itemParent, *itemName, *itemIsCollection, *buffer, *error) {
	*sourcePath = "*itemParent/*itemName";
	*destPath = *buffer.destination;
	if (*sourcePath != *buffer."source") {
		# rewrite path to copy objects that are located underneath the toplevel collection
		*sourceLength = strlen(*sourcePath);
		*relativePath = substr(*sourcePath, strlen(*buffer."source") + 1, *sourceLength);
		*destPath = *buffer."destination" ++ "/" ++ *relativePath;
	}
	if (*itemIsCollection) {
		*error = errorcode(msiCollCreate(*destPath, 1, *status));
	} else {
	 	*error = errorcode(msiDataObjCopy(*sourcePath, *destPath, "verifyChksum=", *status));
	}

}


# \brief iiCopyUserMetadata    Copy user metadata from sourde to destination
# \param[in] source
# \param[in] destination
iiCopyUserMetadata(*source, *destination) {
	*userMetadataPrefix = UUUSERMETADATAPREFIX ++ "%";
	foreach(*row in SELECT META_COLL_ATTR_NAME, META_COLL_ATTR_VALUE
			WHERE COLL_NAME = *source
			AND META_COLL_ATTR_NAME like *userMetadataPrefix) {
		msiString2KeyValPair("", *kvp);
		msiAddKeyVal(*kvp, *row.META_COLL_ATTR_NAME, *row.META_COLL_ATTR_VALUE);
		msiAssociateKeyValuePairsToObj(*kvp, *destination, "-C");
	}
}


# \brief iiCopyActionLog   Copy the action log from the source to destination
# \param[in] source
# \param[in] destination
iiCopyActionLog(*source, *destination) {
	*actionLog = UUORGMETADATAPREFIX ++ "action_log";	
	foreach(*row in SELECT META_COLL_ATTR_NAME, META_COLL_ATTR_VALUE
	       		WHERE META_COLL_ATTR_NAME = *actionLog
		       	AND COLL_NAME = *source) {
		msiString2KeyValPair("", *kvp);
		msiAddKeyVal(*kvp, *row.META_COLL_ATTR_NAME, *row.META_COLL_ATTR_VALUE);
		msiAssociateKeyValuePairsToObj(*kvp, *destination, "-C");
	}
}
