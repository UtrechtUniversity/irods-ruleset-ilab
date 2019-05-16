# \file      iiArchive.r
# \brief     This file contains rules related to archiving a published datapackage

# \author    Lazlo Westerhof
# \copyright Copyright (c) 2017-2018, Utrecht University. All rights reserved.
# \license   GPLv3, see LICENSE.



# \brief Routine to watch status of given datapackage that is in archival process.
# 	 If this is finished successfully, the
#	 - org_vault_status of datapackage is set to ARCHIVED
#        - corresponding datamanager is notified via mail. 
#
# \param[in] vaultPackage       path to published package in the vault to be arhived
# \param[out] status            status of the publication
#
iiProcessArchiveRequestPending(*vaultPackage, *status) {
        # ER IS NU EEN BAG DIE IS AANGEBODEN.
	# ER DIENT DUS EEN url aanwezig te zijn

	*status = "Unknown";

        # Check preconditions
        iiVaultStatus(*vaultPackage, *vaultStatus);
        if (*vaultStatus != PENDING_ARCHIVE_REQUEST) {
                *status = "NotAllowed";
                succeed;
        }

        # PROGRESSION CHECK regarding transfer to DANS - SWORD2 client
	# Use sWORD2 client library to track progress
        # Collect archive_url and based on that, check status.
        *attrArchiveUrl = UUORGMETADATAPREFIX ++ "archive_status_url";
        foreach(*row in SELECT META_COLL_ATTR_VALUE WHERE COLL_NAME = *vaultPackage AND META_COLL_ATTR_NAME = *attrArchiveUrl) {
		*statementURI = *row.META_COLL_ATTR_VALUE;
		break;
        }

	writeLine('serverLog', 'PENDING statementURI: ' ++ *statementURI);

        *sword2Status = '';
        iiRuleSword2Status(*statementURI, *sword2Status, *status);	
        #iiRuleSword2Status(*statementURI, *sword2Status, *status); 
	if (*status != 'Success') {
            writeLine('serverLog', 'Sword2 tech status=' ++ *status);
	    succeed;
        }

	writeLine('serverLog', 'Ultimate Sword2Status=' ++ *sword2Status);

	succeed;

        # Only if *sword2status=ARCHIVED finalize all. All other statuses require waiting.
        # Error statuses (FAILED,INVALID, REJECTED) -> org_vault_status remains PENDING_ARCHIVE_REQUEST 
        if (*sword2Status=='ARCHIVED') {	
	    # Set package vault_status to 'ARCHIVED'
            msiString2KeyValPair("", *kvp);
            msiAddKeyVal(*kvp, UUORGMETADATAPREFIX ++ 'vault_status', ARCHIVED);
            *err = msiSetKeyValuePairsToObj( *kvp, *vaultPackage, "-C");
            if (*err!=0 ) {
                *status = 'InternalError';
                succeed;
            }

            # All is well so notify datamanager by mail (use org_publication_approval_actor)

            # retrieve package title for notifications.
	    *title = "";
	    *titleKey = UUUSERMETADATAPREFIX ++ "0_Title";
	    foreach(*row in SELECT META_COLL_ATTR_VALUE WHERE COLL_NAME = *vaultPackage AND META_COLL_ATTR_NAME = *titleKey) {
                *title = *row.META_COLL_ATTR_VALUE;
		break;
	    }
	    writeLine('stdout', *title);

            # retrieve datamanager based on metadata_attr = org_publication_approval_actor
            *datamanager = "";
            *actorKey = UUORGMETADATAPREFIX ++ "publication_approval_actor";
            foreach(*row in SELECT META_COLL_ATTR_VALUE WHERE COLL_NAME = *vaultPackage AND META_COLL_ATTR_NAME = *actorKey) {
              	*userNameAndZone = *row.META_COLL_ATTR_VALUE;
                uuGetUserAndZone(*userNameAndZone, *datamanager, *zone);
                break;
            }
	    writeLine('stdout', *datamanager);


            # retrieve yodaDOI - must become DANS DOI!! org_publication_yodaDOI
            *yodaDOI = "";
            *yodaDOIKey = UUORGMETADATAPREFIX ++ "publication_yodaDOI";
            foreach(*row in SELECT META_COLL_ATTR_VALUE WHERE COLL_NAME = *vaultPackage AND META_COLL_ATTR_NAME = *yodaDOIKey) {
                *yodaDOI = *row.META_COLL_ATTR_VALUE;
                break;
            }
	    writeLine('serverLog', *yodaDOI);


            uuNewArchivedPackageMail(*datamanager, uuClientFullName, *title, *yodaDOI, *mailStatus, *message);
            if (int(*mailStatus) != 0) {
                writeLine("serverLog", "iiProcessArchiveRequestPending: Datamanager notification failed: *message");
            }
        }
	*status = 'Success';
}


# \brief Routine to start archiving given published vaultpackage
# This will change org_vault_status to PENDING_ARCHIVE_REQUEST
#
# \param[in] vaultPackage       path to published package in the vault to be archived
# \param[out]
iiProcessArchiveRequest(*vaultPackage, *status) {
        writeLine('serverLog', 'START:ProcessArchiveRequest: ' ++ *vaultPackage);
	*status = "Unknown";

        *uniqueMaker = '';
	# Used in collection name on virtual disk under /archives/*uniqueMakes
        # As well as the bagit name (as this is bagit name is used on physical drive as well.
	# On physical drive all bagits are collected within one folder and that requires for the bagit names to be unique as well
        foreach(*row in SELECT COLL_ID WHERE COLL_NAME = *vaultPackage) {
		*uniqueMaker =  *row.COLL_ID;
                break;
        }
	if(*uniqueMaker == '') {
		*status = 'NoCollectionID';
		succeed;
	}

        # Check preconditions - must have status ARCHIVE_REQUEST
        iiVaultStatus(*vaultPackage, *vaultStatus);
        if (*vaultStatus != ARCHIVE_REQUEST) {
                *status = "NotAllowed";
                succeed;
        }

        # BAGIT CREATION
        # Create bagit from *vaultPackage
	*bagitPath = '/tempZone/yoda/archives/*uniqueMaker/*uniqueMaker' ++ 'bagit.tar';  # naam en folder gebaseerd op ID package?
	iiRuleCreateBagit(*vaultPackage, *bagitPath, *status);
        if (*status != 'Success') {
	    *status = "ErrorCreatingBagit"; # mss hier gelijk de status overnemen van iiRuleBagit
	    succeed;
        }
	# Add KVP org_archive_bagit_irods_path to *vaultPackage
        msiString2KeyValPair("", *kvp);
        msiAddKeyVal(*kvp, UUORGMETADATAPREFIX ++ 'archive_bagit_irods_path', *bagitPath);

        *err = msiSetKeyValuePairsToObj( *kvp, *vaultPackage, "-C");
        if (*err!=0 ) {
                *status = 'InternalError';
                succeed;
        }
	

	# COPY BAGIT TO FILE SYSTEM
        # Physical copy to system in order for SWORD2 to be able to transfer it to DANS EASY 
	*bagitPhysicalPath = '/etc/irods/irods-ruleset-research/tools/*uniqueMaker' ++ 'bagit.tar';  
        iiRuleCopyDataObjectToFileSystem(*bagitPath, *bagitPhysicalPath, *status);
        if (*status != 'Success') {
            *status = "ErrorCreatingBagit"; # mss hier gelijk de status overnemen van iiRuleBagit
            succeed;
        }
        # Add KVP org_archive_bagit_physical_path to *vaultPackage
        msiString2KeyValPair("", *kvp);
        msiAddKeyVal(*kvp, UUORGMETADATAPREFIX ++ 'archive_bagit_physical_path', *bagitPhysicalPath);

        *err = msiSetKeyValuePairsToObj( *kvp, *vaultPackage, "-C");
        if (*err!=0 ) {
                *status = 'InternalError';
                succeed;
        }

        writeLine('serverLog', 'iRODS-beforeSWORD2');
	# TRANSFER TO DANS ACT EASY USING SWORD2 INTERFACE
        # User SWORD2 library to start archiving at DANS
        # This can be asynchronous from creating the bag - maybe do this under 'PENDING_ARCHIVE_REQUEST' handling?
        *urlArchiveStatus = '';
        iiRuleSword2Transfer(*bagitPhysicalPath, *urlArchiveStatus, *status);
        if (*status != 'Success') {
            *status = "ErrorStartingBagTransfer";  # mss hier gelijk status uit iiRuleSword2
            succeed;
        }

	# Bag has been offered to DANS.
	# the archival url needs to be save for polling the progress
        msiString2KeyValPair("", *kvp);
        msiAddKeyVal(*kvp, UUORGMETADATAPREFIX ++ 'archive_status_url', *urlArchiveStatus);

        *err = msiSetKeyValuePairsToObj( *kvp, *vaultPackage, "-C");
        if (*err!=0 ) {
                *status = 'InternalError';
                succeed;
        }
	writeLine('serverLog', 'END:ProcessArchiveRequest: ' ++ *vaultPackage);


        #succeed;

	# All preperation is done. 
	# Change status to 'PENDING'
	msiString2KeyValPair("", *kvp);
        msiAddKeyVal(*kvp, UUORGMETADATAPREFIX ++ 'vault_status', PENDING_ARCHIVE_REQUEST);

	*err = msiSetKeyValuePairsToObj( *kvp, *vaultPackage, "-C");
	if (*err!=0 ) {
                *status = 'InternalError';
                succeed;
        }

	*status = 'Success';
}





