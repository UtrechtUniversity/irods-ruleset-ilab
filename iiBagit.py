# \file      iiBagit.py
# \brief     Functions for Bagit functionality for archiving purposes
# \author    Lazlo Westerhof
# \copyright Copyright (c) 2018-2019 Utrecht University. All rights reserved.
# \license   GPLv3, see LICENSE.



#--------------------- Interface layer from irods rules

#\ iiRuleCreateBagit
#\ Brief create a bagit, a tar file conform the bagit standard
#\[in]   rule_args[0] vaultPackage  => collection!!!
#\[in]   rule_args[1] bagitPath     => collection!!!
#\[out]  rule_args[2] status

def iiRuleCreateBagit(rule_args, callback, rei):
    packagePath = rule_args[0]
    bagitPath = rule_args[1]

    rule_args[2] = createBagit(callback, packagePath, bagitPath)

#\ iiRuleCopyDataObjectToFileSystem
#\ Brief create a physical copy of the bagit with location bagitPath to physical location
#\[in]  rule_args[0] irodsDataObjectPath
#\[in]  rule_args[1] physicalDestination
#\[out]  rule_args[2] status

def iiRuleCopyDataObjectToFileSystem(rule_args, callback, rei):
    irodsDataObjectPath = rule_args[0]
    physicalDestination = rule_args[1]
    
    rule_args[2] = copyDataObjectToFileSystem(callback, irodsDataObjectPath, physicalDestination)


#\ iiRuleSword2
#\ Brief transfer a bagit to dans and retrieve a url for polling of transfer status
#\[in]   rule_args[0] bagitPhysicalPath
#\[out]  rule_args[1] statementURI
#\[out]  rule_args[2] status

def iiRuleSword2(rule_args, callback, rei):
    bagitPhysicalPath = rule_args[0]

    response = doSwordit(callback, bagitPhysicalPath)

    callback.writeLine('serverLog', 'SWORD')

    rule_args[1] = response['statementURI']
    rule_args[2] = response['status'] 


#--------------------- End of interface layer from irods rules
# *BAGITDATA="/tempZone/home/rods/sub1", 
# *NEWBAGITROOT="/tempZone/home/rods/bagit"


def doSwordit(callback, bagitFile):
    zipFile = bagitFile
    SD_URI = 'https://act.easy.dans.knaw.nl/sword2/collection/1'

    response = {}
    response['status'] = 'Unknown'
    response['statementURI'] = ''

    from sword2 import Connection

    from sword2 import http_layer    
    http_impl = http_layer.HttpLib2Layer("/var/lib/irods", timeout=30.0, ca_certs=None)

    callback.writeLine('serverLog', 'AFter http_impl')

    from sword2 import sword2_logging
    #sword2_logging.create_logging_config(None)

    callback.writeLine('serverLog', 'SWORD2 before connection')

    c = Connection(SD_URI, user_name = "yodatest", user_pass="PLACEHOLDER", http_impl = http_impl)
    
    callback.writeLine('serverLog', 'SWORD2 after connection')
   
    with open(bagitFile, "r") as pkg:
        receipt = c.create(col_iri = SD_URI,
                                payload = pkg,
                                mimetype = "application/tar",
                                filename = "package.tar",
                                packaging = 'http://purl.org/net/sword/package/Binary',
                                in_progress = False)    # As the deposit isn't yet finished

        callback.writeLine('serverLog', '[SWORD2]se iri=' + receipt.se_iri)
        callback.writeLine('serverLog', '[SWORD2]media iri=' + receipt.edit_media)

        callback.writeLine('serverLog', '[SWORD2]edit iri=' + receipt.edit)

        callback.writeLine('serverLog', '##################')
        #callback.writeLine('serverLog', receipt.links)

        callback.writeLine('serverLog', '#########')
        callback.writeLine('serverLog', 'StatementURI = ' )
        callback.writeLine('serverLog', receipt.links['http://purl.org/net/sword/terms/statement'][0]['href'])
        statementURI = receipt.links['http://purl.org/net/sword/terms/statement'][0]['href']

        response['status'] = 'Success'
        response['statementURI'] = statementURI

        return response

        #callback.writeLine('serverLog', receipt.content)

        #c2 = Connection(statementURI, user_name = "yodatest", user_pass="PLACEHOLDER", http_impl = http_impl)
        #resp = c2.get_resource(statementURI)
        #callback.writeLine('serverLog', resp)

        #    `ContentWrapper.response_headers`    -- response headers
        #    `ContentWrapper.content` -- body of response from server (the file or package)
        #    `ContentWrapper.code`    -- status code ('200' on success.)


        #callback.writeLine('serverLog', '::::::::::::HEADERS :::::::::::::')
        #callback.writeLine('serverLog', resp.response_headers)
        #callback.writeLine('serverLog', ':::::::::::CONTENT::::::::::::::')
        #callback.writeLine('serverLog', resp.content)
        #callback.writeLine('serverLog', '::::::::::CODE:::::::::::::::')
        #callback.writeLine('serverLog', resp.code)

    response['status'] = 'ErrorSWORD2'
    
    return response


def followSwordTransfer(callback):
    url = 'http://blabla'


def copyDataObjectToFileSystem(callback, irodsSourcePath, physicalDestination):
    ret_val = {}

    ret_val = callback.msiDataObjOpen('objPath=' + irodsSourcePath, 0)
    fd = ret_val['arguments'][1]

    ret_val = callback.msiDataObjRead(fd, 5000000, irods_types.BytesBuf())
    bytesBuf = ret_val['arguments'][2]

    callback.writeLine('stdout', str(bytesBuf.len))

    f = open(physicalDestination, "wb")
    f.write(bytearray(bytesBuf.buf))
    f.close()

    return 'Success'



def createBagit(callback, packagePath, bagitPath):
    bagIt_data = '/tempZone/home/vault-initial/research-initial[1556270526]'
    # new_bagIt_root = '/tempZone/home/research-initial/research-initial[1556270526]-bag'   
 
    # get bagit filename and root based upon bagitPath
    import os
    (new_bagIt_root, tar_file_name) = os.path.split(bagitPath)  #e.g. bagitPath = /tempZone/yoda/archives/123/bagit.tar

    new_bagIt_root = new_bagIt_root + '/bagData'
    callback.writeLine('stdout', new_bagIt_root)
    callback.writeLine('stdout', tar_file_name)

    # Create NEWBAGITROOT collection
    callback.msiCollCreate(new_bagIt_root, '1', 0)

    offset = len(new_bagIt_root) + 1

    # Clear buffer so far
    callback.msiFreeBuffer('stdout')

    # Write bagit.txt to NEWBAGITROOT/bagit.txt
    callback.writeLine('stdout', 'BagIt-Version: 0.96')
    callback.writeLine('stdout', 'Tag-File-Character-Encoding: UTF-8')
    ret_val = callback.msiDataObjCreate(new_bagIt_root + '/bagit.txt', 'forceFlag=1', 0)
    fd = ret_val['arguments'][2]
    callback.msiDataObjWrite(fd, 'stdout', 0)
    callback.msiDataObjClose(fd, 0)
    callback.msiFreeBuffer('stdout')


    # Rsyncs existing *BAGITDATA to NEWBAGITROOT/data
    new_bagIt_data = new_bagIt_root + '/data'
    callback.msiCollRsync(bagIt_data, new_bagIt_data, 'null', 'IRODS_TO_IRODS', 0)

    # Rsyncs existing fake metadata  to NEWBAGITROOT/metadadata
    new_bagIt_metadata = new_bagIt_root + '/metadata'
    callback.msiCollRsync('/tempZone/yoda/archives/xml', new_bagIt_metadata, 'null', 'IRODS_TO_IRODS', 0)


    # Generates payload manifest file of NEWBAGITROOT/data
    continue_index_old = 1
    condition = "COLL_NAME like '" + new_bagIt_data + "%%'"
    ret_val = callback.msiMakeGenQuery('DATA_ID, DATA_NAME, COLL_NAME', condition, irods_types.GenQueryInp())
    genQueryInp = ret_val['arguments'][2]
    ret_val = callback.msiExecGenQuery(genQueryInp, irods_types.GenQueryOut())
    genQueryOut = ret_val['arguments'][1]

    while continue_index_old > 0:
        for row in range(genQueryOut.rowCnt):
            data = genQueryOut.sqlResult[1].row(row)
            coll = genQueryOut.sqlResult[2].row(row)
            full_path = coll + '/' + data
            relative_path = full_path[offset:]
            ret_val = callback.msiDataObjChksum(full_path, 'forceChksum=', 'dummy_str')
            chksum = ret_val['arguments'][2]
            callback.writeLine('stdout', relative_path + '   ' + chksum)
        continue_index_old = genQueryOut.continueInx
        if continue_index_old > 0:
            ret_val = callback.msiGetMoreRows(genQueryInp, genQueryOut, 0)
            genQueryOut = ret_val['arguments'][1]

    # Write payload manifest to NEWBAGITROOT/manifest-sha2.txt
    ret_val = callback.msiDataObjCreate(new_bagIt_root + '/manifest-sha2.txt', 'forceFlag=1', 0)
    fd = ret_val['arguments'][2]
    callback.msiDataObjWrite(fd, 'stdout', 0)
    callback.msiDataObjClose(fd, 0)
    callback.msiFreeBuffer('stdout')


    # Write tagmanifest file to NEWBAGITROOT/tagmanifest-sha2.txt 
    # bag-info.txt MIST - required?
    
    # bagit.txt
    ret_val = callback.msiDataObjChksum(new_bagIt_root + '/bagit.txt', 'forceChksum', 'dummy_str')
    chksum = ret_val['arguments'][2]
    callback.writeLine('stdout', 'bagit.txt   ' + chksum)
    
    # manifest-md5.txt
    ret_val = callback.msiDataObjChksum(new_bagIt_root + '/manifest-sha2.txt', 'forceChksum', 'dummy_str')
    chksum = ret_val['arguments'][2]
    callback.writeLine('stdout', 'manifest-sha2.txt   ' + chksum)
    
    # metadata/dataset.xml
    ret_val = callback.msiDataObjChksum(new_bagIt_root + '/metadata/dataset.xml', 'forceChksum', 'dummy_str')
    chksum = ret_val['arguments'][2]
    callback.writeLine('stdout', 'metadata/dataset.xml   ' + chksum)

    # metadata/files.xml is missing. - required?

    # TAGMANIFEST: Write entire stdout buffer in tagminifest-sha2,txt
    ret_val = callback.msiDataObjCreate(new_bagIt_root + '/tagmanifest-sha2.txt', 'forceFlag=1', 0)
    fd = ret_val['arguments'][2]
    callback.msiDataObjWrite(fd, 'stdout', 0)
    callback.msiDataObjClose(fd, 0)
    callback.msiFreeBuffer('stdout')

    # Create tarfile of new bag for faster download
    #tar_file_path = new_bagIt_root + tar_file_name
    #callback.msiTarFileCreate(tar_file_path, new_bagIt_root, 'null', 'forceFlag=1')
    callback.msiTarFileCreate(bagitPath, new_bagIt_root, 'null', 'forceFlag=1')

    # trick to be able to access easliy through webDav
    visiblePath = '/tempZone/home/research-initial/bag2.tar' 
    callback.msiTarFileCreate(visiblePath, new_bagIt_root, 'null', 'forceFlag=1')


    return 'Success'


    # Get filesize of new tarfile
    import os
    (coll, tar_file_name) = os.path.split(tar_file_path)

    condition = "COLL_NAME like '" + coll + "%%' and DATA_NAME = '" + tar_file_name + "'"
    ret_val = callback.msiMakeGenQuery('DATA_SIZE', condition, irods_types.GenQueryInp())
    genQueryInp = ret_val['arguments'][2]
    ret_val = callback.msiExecGenQuery(genQueryInp, irods_types.GenQueryOut())
    genQueryOut = ret_val['arguments'][1]


    print_size = 0
    print_unit = ''


    for row in range(genQueryOut.rowCnt):
        data_size = int(genQueryOut.sqlResult[0].row(row))
        if data_size > 1048576:
            print_size = data_size / 1048576
            print_unit = 'MB'
        else:
            if data_size > 1024:
                print_size = data_size / 1024
                print_unit = 'KB'
            else:
                print_size = data_size
                print_unit = 'B'

    # Output report and suggested download procedures
    callback.writeLine('stdout', '\nYour BagIt bag has been created and tarred on the iRODS server:')
    callback.writeLine('stdout', '  ' + new_bagIt_root + '.tar - ' + str(print_size) + ' ' + print_unit)
    callback.writeLine('stdout', '\nTo copy it to your local computer, use:')
    callback.writeLine('stdout', '  iget -Pf ' + new_bagIt_root + '.tar ' + tar_file_name + '\n')

    # Write to rodsLog
    callback.writeLine('serverLog', 'BagIt bag created: ' + new_bagIt_root + ' <- ' + bagIt_data)

#INPUT *BAGITDATA="/tempZone/home/rods/sub1", *NEWBAGITROOT="/tempZone/home/rods/bagit"
#OUTPUT ruleExecOut


