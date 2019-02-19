# \file      iiVault.py
# \brief     Functions to copy packages to the vault and manage permissions of vault packages.
# \author    Lazlo Westerhof
# \copyright Copyright (c) 2019 Utrecht University. All rights reserved.
# \license   GPLv3, see LICENSE.

import json
import os


# \brief Retrieve lists of preservable file formats on the system.
#
# \return Lists of preservable file formats
#
def getPreservableFormatsLists(callback):
    preservableLists = {}

    ret_val = callback.msiMakeGenQuery(
        "DATA_NAME, COLL_NAME",
        "COLL_NAME = '/tempZone/yoda/file_formats' AND DATA_NAME like '%%.json'",
        irods_types.GenQueryInp())
    query = ret_val["arguments"][2]

    ret_val = callback.msiExecGenQuery(query, irods_types.GenQueryOut())
    while True:
        result = ret_val["arguments"][1]
        for row in range(result.rowCnt):
            data_name = result.sqlResult[0].row(row)
            coll_name = result.sqlResult[1].row(row)

            # Retrieve filename and name of list.
            filename, file_extension = os.path.splitext(data_name)
            json = parseJson(callback, coll_name + "/" + data_name)
            name = json['name']
            callback.writeLine("serverLog", str(name))

        if result.continueInx == 0:
            break
        ret_val = callback.msiGetMoreRows(query, result, 0)
    callback.msiCloseGenQuery(query, result)

    return {'lists': {'DANS': 'DANS Preservable formats', '4TU': '4TU Preservable formats'}}


# \brief Retrieve all unpreservable files in a folder.
#
# \param[in] folder Path of folder to check.
# \param[in] list   Name of preservable file format list.
#
# \return List of unpreservable files.
#
def getUnpreservableFiles(callback, folder, list):
    # Retrieve JSON list of preservable file formats.
    json = parseJson(callback, "/tempZone/yoda/file_formats/" + list + ".json")
    preservableFormats = json['formats']
    unpreservableFormats = []

    ret_val = callback.msiMakeGenQuery(
        "DATA_NAME, COLL_NAME",
        "COLL_NAME like '%s%%'" % (folder),
        irods_types.GenQueryInp())
    query = ret_val["arguments"][2]

    ret_val = callback.msiExecGenQuery(query, irods_types.GenQueryOut())
    while True:
        result = ret_val["arguments"][1]
        for row in range(result.rowCnt):
            data_name = result.sqlResult[0].row(row)
            filename, file_extension = os.path.splitext(data_name)

            # Convert to lowercase and remove dot.
            file_extension = (file_extension.lower())[1:]

            # Check if extention is in preservable format list.
            if (file_extension not in preservableFormats):
                unpreservableFormats.append(file_extension)

        if result.continueInx == 0:
            break
        ret_val = callback.msiGetMoreRows(query, result, 0)
    callback.msiCloseGenQuery(query, result)

    return {'formats': unpreservableFormats}


# \brief Write preservable file formats lists to stdout.
#
def iiGetPreservableFormatsListsJson(rule_args, callback, rei):
    callback.writeString("stdout", json.dumps(getPreservableFormatsLists(callback)))


# \brief Write unpreservable files in folder to stdout.
#
# \param[in] rule_args[0] Path of folder to check.
# \param[in] rule_args[1] Name of preservable file format list.
#
def iiGetUnpreservableFilesJson(rule_args, callback, rei):
    callback.writeString("stdout", json.dumps(getUnpreservableFiles(callback, rule_args[0], rule_args[1])))