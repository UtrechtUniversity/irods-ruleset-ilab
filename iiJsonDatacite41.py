from json import loads
from collections import OrderedDict


# Waar komt de json string vandaan
# Waar gaat de het resultaat heen???





# \brief Frontend function to add action log record to specific folder
#
# \param[in] actor     rodsaccount coming from yoda frontend
# \param[in] folder    folder the logging is linked to
# \param[in] action    the text that is logged

def iiCreateCombiMetadataJson(rule_args, callback, rei):
    actor, folder, action = rule_args[0:3]

    metadataJsonPath, combiJsonPath, lastModifiedDateTime, yodaDOI, publicationDate, openAccessLink, licenseUri = rule_args[0:7]

    metaDict = getYodaMetadaJsonDict(callback, metadataJsonPath)

    metaDict['System'] = {} 

    # write combined data to file
    ret_val = callback.msiDataObjCreate(combiJsonPath, ofFlags, 0)
    
    #copyACLsFromParent(callback, combiJsonPath, "default")

    fileHandle = ret_val['arguments'][2]
    callback.msiDataObjWrite(fileHandle, json.dumps(metaDict), 0)
    callback.msiDataObjClose(fileHandle, 0)




# \brief Get yodametadata Json and return as (ordered!) dict
#
# \param[in] yoda_json_path
#
# \return dict hodling the content of yoda-metadata.json
#
def getYodaMetadaJsonDict(callback, yoda_json_path):

    coll_name, data_name = os.path.split(yoda_json_path)

    data_size = getDataObjSize(callback, coll_name, data_name)

    # Open JSON file
    ret_val = callback.msiDataObjOpen('objPath=' + yoda_json_path, 0)
    fileHandle = ret_val['arguments'][1]

    # Read JSON
    ret_val = callback.msiDataObjRead(fileHandle, data_size, irods_types.BytesBuf())

    # Close JSON
    callback.msiDataObjClose(fileHandle, 0)

    # Parse JSON into dict.
    read_buf = ret_val['arguments'][2]
    jsonText = ''.join(read_buf.buf)

    # Use the hook to keep ordering of elements as in metadata.json
    return json.loads(jsonText, object_pairs_hook=OrderedDict)



# \brief Get metadata formatted as datacite XML
#
# \param[in] json string containing metadata from YoDa
#
# \return string containing metadata formatted as datacite XML
# 
def dataciteXml(jsonString):
#    print('===================XML for datacite=================')

    dict = json.loads(jsonString)

    #print(dict['Descriptive-group'])

    # Build datacite XML as string
    #getHeader()
    print(getDOI(dict))


    print(getTitles(dict))
    print(getDescriptions(dict))
    print(getPublisher(dict))
    print(getPublicationYear(dict))
    print(getSubjects(dict))

    print(getCreators(dict))
    print(getContributors(dict))
    print(getDates(dict))
    print(getVersion(dict))
    print(getRightsList(dict))
    print(getLanguage(dict))
    print(getResourceType(dict))
    print(getRelatedDataPackage(dict))

    print(getGeoLocations(dict))
    print(getFunders(dict))




def getHeader(): # all that is present before the yoda data  !! Hier moet de ID nog in
    return 'Blablablabla:'

def getDOI(dict):
    # <identifier identifierType="DOI">
    #       <xsl:value-of select="yoda:System/yoda:Persistent_Identifier_Datapackage[yoda:Identifier_Scheme='DOI']/yoda:Identifier"/>
    #    </identifier>
    doi = dict['System']['Persistent_Identifier_Datapackage']['Identifier']

    return '<identifier identifierType="DOI">' +  doi + '</identifier>'


def getTitles(dict):
      #   <titles>
      #     <xsl:apply-templates select="yoda:Title"/>
      #   </titles>
      # <xsl:template match="yoda:Title">
      #    <title>
      #      <xsl:attribute name="xml:lang">
      #       <xsl:value-of select="substring(../yoda:Language,1,2)"/>
      #     </xsl:attribute>
      #        <xsl:value-of select="." />
      #     </title>
      # </xsl:template>

    language = dict['Descriptive-group']['Language'][0:2]
    title = dict['Descriptive-group']['Title']

    return '<titles><title xml:lang="' + language + '">' + title + '</title></titles>'

def getDescriptions(dict):
    #     <descriptions>
    #       <description descriptionType="Abstract">
    #           <xsl:value-of select="yoda:Description"/>
    #       </description>
    #     </descriptions><

    description = dict['Descriptive-group']['Description']
    return '<descriptions><description descriptionType="Abstract">' + description + '</description></descriptions>'


def getPublisher(dict):
    # <publisher>Utrecht University</publisher>

    return '<publisher>Utrecht University</publisher>'

def getPublicationYear(dict):
#        <publicationYear>
#           <xsl:apply-templates select="yoda:System/yoda:Publication_Date"/>
#        </publicationYear>
#
#              <xsl:template match="yoda:System/yoda:Publication_Date">
#              <!--
#                The date is in YYYY-MM-DD form, so we need to extract the first 4 digits for the year.
#                xslt substring indexes start at 1 -->
#              <xsl:value-of select="substring(., 1, 4)" />
#              </xsl:template>

    publicationYear = '2019'
    return '<publicationYear>' + publicationYear + '</publicationYear>'


def getSubjects(dict):
#        <xsl:if test="yoda:Discipline or yoda:Tag">
#          <subjects>
#            <xsl:apply-templates select="yoda:Discipline"/>
#            <xsl:apply-templates select="yoda:Tag"/>
#          </subjects>
#        </xsl:if>
#
#            yoda:Discipline
#              <xsl:template match="yoda:Discipline">
#                    <subject subjectScheme="OECD FOS 2007"><xsl:value-of select="." /></subject>
#              </xsl:template>
#
#            yoda:Tag
#              <xsl:template match="yoda:Tag">
#                       <subject subjectScheme="Keyword"><xsl:value-of select="." /></subject>
#                  </xsl:template>
#

    subjectDisciplines = ''
    subjectTags = ''

    for disc in dict['Descriptive-group']['Discipline']:
        subjectDisciplines = subjectDisciplines + '<subject subjectScheme="OECD FOS 2007">' + disc + '</subject>'

    for tag in dict['Descriptive-group']['Tag']:
        subjectTags = subjectTags + '<subject subjectScheme="Keyword">' + tag + '</subject>'


    return '<subjects>' + subjectDisciplines + subjectTags + '</subjects>'


def getFunders(dict):
#        <xsl:if test="yoda:Funding_Reference">
#          <fundingReferences>
#            <xsl:apply-templates select="yoda:Funding_Reference"/>
#          </fundingReferences>
#        </xsl:if>
#           <fundingReference>
#             <funderName><xsl:value-of select="./yoda:Funder_Name"/></funderName>
#             <xsl:if test="./yoda:Properties/yoda:Award_Number">
#               <awardNumber><xsl:value-of select="./yoda:Properties/yoda:Award_Number"/></awardNumber>
#             </xsl:if>
#           </fundingReference>


    # !!! test if present
    fundingRefs = '';
    for funder in dict['Administrative-group']['Funding_Reference']:
        fundingRefs = fundingRefs + '<fundingReference><funderName>' + funder['Funder_Name'] + '</funderName><awardNumber>' + funder['Award_Number'] + '</awardNumber></fundingReference>'
    return '<fundingReferences>' + fundingRefs + '</fundingReferences>'

def getCreators(dict):
  #       <creators>
  #         <xsl:apply-templates select="yoda:Creator"/>
  #       </creators>
  # <xsl:template match="yoda:Creator">
  #     <creator>
  #        <creatorName><xsl:value-of select="yoda:Name"/></creatorName>
  #        <xsl:apply-templates select="yoda:Properties/yoda:Person_Identifier"/>
  #        <xsl:apply-templates select="yoda:Properties/yoda:Affiliation"/>
  #     </creator>
  # </xsl:template>
  # <xsl:template match="yoda:Properties/yoda:Person_Identifier">
  #       <nameIdentifier>
  #          <xsl:attribute name="nameIdentifierScheme">
  #             <xsl:value-of select="yoda:Name_Identifier_Scheme" />
  #          </xsl:attribute>
  #          <xsl:value-of select="yoda:Name_Identifier" />
  #       </nameIdentifier>
  # </xsl:template>
  #
  # <xsl:template match="yoda:Properties/yoda:Affiliation">
  #       <affiliation><xsl:value-of select="." /></affiliation>
  # </xsl:template>


    creators = ''
    for creator in dict['Rights-group']['Creator']:
      creators = creators + '<creator>'
      creators = creators + '<creatorName>' + creator['Name'] + '</creatorName>'

      # Possibly multiple person identifiers
      listIdentifiers = creator['Person_Identifier']
      nameIdentifiers = ''
      for dictId in listIdentifiers:
          nameIdentifiers = nameIdentifiers + '<nameIdentifier nameIdentifierScheme="' + dictId['Name_Identifier_Scheme'] + '">' + dictId['Name_Identifier'] + '</nameIdentifier>'

      # Possibly multiple affiliations
      affiliations = ''
      for aff in creator['Affiliation']:
          affiliations = affiliations + '<affiliation>' + aff + '</affiliation>'

      creators = creators + nameIdentifiers
      creators = creators + affiliations
      creators = creators + '</creator>'

    return '<creators>' + creators + '</creators>'


def getContributors(dict):
  #       <xsl:if test="yoda:Contributor">
  #           <contributors>
  #               <xsl:apply-templates select="yoda:Contributor"/>
  #           </contributors>
  #       </xsl:if>
  #
  #
  # <xsl:template match="yoda:Contributor">
  #   <contributor>
  #     <xsl:attribute name="contributorType">
  #       <xsl:value-of select="yoda:Properties/yoda:Contributor_Type"/>
  #     </xsl:attribute>
  #     <contributorName><xsl:value-of select="yoda:Name" /></contributorName>
  #     <xsl:apply-templates select="yoda:Properties/yoda:Person_Identifier" />
  #     <xsl:apply-templates select="yoda:Properties/yoda:Affiliation"/>
  #   </contributor>
  # </xsl:template>
  # <xsl:template match="yoda:Properties/yoda:Person_Identifier">
  #       <nameIdentifier>
  #          <xsl:attribute name="nameIdentifierScheme">
  #             <xsl:value-of select="yoda:Name_Identifier_Scheme" />
  #          </xsl:attribute>
  #          <xsl:value-of select="yoda:Name_Identifier" />
  #       </nameIdentifier>
  # </xsl:template>
  #
  # <xsl:template match="yoda:Properties/yoda:Affiliation">
  #       <affiliation><xsl:value-of select="." /></affiliation>
  # </xsl:template>

    contributors = ''
    for contributor in dict['Rights-group']['Contributor']:
        # print(contributor)
        # print(contributor['Name'])
        # print(contributor['Contributor_Type'])

        contributors = contributors + '<contributor contributorType="' + contributor['Contributor_Type'] + '">'
        contributors = contributors + '<contributorName>' + contributor['Name'] + '</contributorName>'

        #Possibly multiple person identifiers
        listIdentifiers = contributor['Person_Identifier']
        nameIdentifiers = ''
        for dictId in listIdentifiers:
            nameIdentifiers = nameIdentifiers + '<nameIdentifier nameIdentifierScheme="' + dictId['Name_Identifier_Scheme'] + '">' + dictId['Name_Identifier'] + '</nameIdentifier>'

        # Possibly multiple affiliations
        affiliations = ''
        for aff in contributor['Affiliation']:
            affiliations = affiliations + '<affiliation>' + aff + '/affiliation>'

        contributors = contributors + nameIdentifiers
        contributors = contributors + affiliations
        contributors = contributors + '</contributor>'

    return '<contributors>' + contributors + '</contributors>'

def getDates(dict):
    # <dates>
    #   <xsl:if test="yoda:System/yoda:Last_Modified_Date">
    #     <date dateType="Updated"><xsl:value-of select="yoda:System/yoda:Last_Modified_Date"/></date>
    #   </xsl:if>
    #   <xsl:if test="yoda:Embargo_End_Date">
    #     <date dateType="Available"><xsl:value-of select="yoda:Embargo_End_Date"/></date>
    #   </xsl:if>
    #   <xsl:if test="yoda:Collected">
    #     <date dateType="Collected"><xsl:value-of select="yoda:Collected/yoda:Start_Date" />/<xsl:value-of select="yoda:Collected/yoda:End_Date"/></date>
    #   </xsl:if>
    # </dates>

    dates = ''
    dateModified = dict['System']['Last_Modified_Date']
    dates = dates + '<date dateType="Updated">' + dateModified + '</date>'

    dateEmbargoEnd = dict['Administrative-group']['Embargo_End_Date']
    dates = dates + '<date dateType="Availlable">' + dateEmbargoEnd + '</date>'

    dateCollectStart = dict['Descriptive-group']['Collected']['Start_Date']
    dateCollectEnd = dict['Descriptive-group']['Collected']['End_Date']
    dates = dates + '<date dateType="Collected">' + dateCollectStart + ' / ' + dateCollectEnd + '</date>'

    return '<dates>' + dates + '</dates>'

def getVersion(dict):
    #   xsl:apply-templates select="yoda:Version"/>
    #  <xsl:template match="yoda:Version">
    #      <version><xsl:value-of select="."/></version>
    #   </xsl:template>
    #
    version = dict['Descriptive-group']['Version']
    return '<version>' + version + '</version>'

def getRightsList(dict):
        # <rightsList>
        #   <xsl:apply-templates select="yoda:License"/>
        #   <xsl:apply-templates select="yoda:Data_Access_Restriction"/>
        # </rightsList>
        #
        #     <xsl:template match="yoda:License">
        #       <rights>
        #          <xsl:if test="/yoda:metadata/yoda:System/yoda:License_URI">
        #            <xsl:attribute name="rightsURI"><xsl:value-of select="/yoda:metadata/yoda:System/yoda:License_URI"/></xsl:attribute>
        #          </xsl:if>
        #          <xsl:value-of select="." />
        #       </rights>
        #     </xsl:template>
        #
        #     <xsl:template match="yoda:Data_Access_Restriction[starts-with(.,'Open')]">
        #       <rights><xsl:attribute name="rightsURI">info:eu-repo/semantics/openAccess</xsl:attribute>Open Access</rights>
        #     </xsl:template>
        #     <xsl:template match="yoda:Data_Access_Restriction[starts-with(.,'Restricted')]">
        #       <rights><xsl:attribute name="rightsURI">info:eu-repo/semantics/restrictedAccess</xsl:attribute>Restricted Access</rights>
        #     </xsl:template>
        #     <xsl:template match="yoda:Data_Access_Restriction[.='Closed']">
        #       <rights><xsl:attribute name="rightsURI">info:eu-repo/semantics/closedAccess</xsl:attribute>Closed Access</rights>
        #     </xsl:template>


    licenseURI = dict['System']['License_URI']
    rights = '<rights rightsURI="' + licenseURI + '"></rights>'

    accessRestriction = dict['Rights-group']['Data_Access_Restriction']

    accessOptions = {'Open': 'info:eu-repo/semantics/openAccess', 'Restricted': 'info:eu-repo/semantics/restrictedAccess' , 'Closed': 'info:eu-repo/semantics/closedAccess'}

    rightsURI = ''
    for option,uri in accessOptions.items():
        # print(option)
        # print(uri)
        if accessRestriction.startswith(option):
            rightsURI = uri
            break

    rights = rights + '<rights rightsURI="' + rightsURI + '"></rights>'

    return '<rightslist>' + rights + '</rightslist>'

def getLanguage(dict):
    ''' <language><xsl:value-of select="substring(yoda:Language, 1, 2)"/></language>'''
    language = dict['Descriptive-group']['Language'][0:2]
    return '<language>' + language + '</language>'

def getResourceType(dict):
        #     <resourceType>
        #     <xsl:attribute name="resourceTypeGeneral">
        #         <xsl:value-of select="yoda:Data_Type" />
        #     </xsl:attribute>
   	  #       <xsl:choose>
        #       <xsl:when test="yoda:Data_Type = 'Dataset'">
        #           Research Data
        #       </xsl:when>
        #       <xsl:when test="yoda:Data_Type = 'Datapaper'">
        #           Method Description
        #       </xsl:when>
        #       <xsl:when test="yoda:Data_Type = 'Software'">
        #           Computer Code
        #       </xsl:when>
        #       <xsl:otherwise>
        #           Other Document
        #       </xsl:otherwise>
        #     </xsl:choose>
        # </resourceType>
    yodaResourceToDatacite = {'Dataset': 'Research Data', 'Datapaper': 'Method Description', 'Software': 'Computer code'}
    yodaResourceType = dict['Administrative-group']['Data_Type']

    try:
        dataciteType = yodaResourceToDatacite[yodaResourceType]
    except KeyError:
        dataciteType = 'Other Document'

    return '<resourceType>' + dataciteType + '</resourceType>'


def getRelatedDataPackage(dict):

#         <xsl:if test="(yoda:Related_Datapackage/yoda:Properties/yoda:Persistent_Identifier/yoda:Identifier) and (yoda:Related_Datapackage/yoda:Relation_Type)">
#           <relatedIdentifiers>
#             <xsl:apply-templates select="yoda:Related_Datapackage"/>
#           </relatedIdentifiers>
#         </xsl:if>
# <xsl:template match="yoda:Related_Datapackage">
#
#    <xsl:if test="(yoda:Properties/yoda:Persistent_Identifier/yoda:Identifier) and (yoda:Relation_Type)">
#       <relatedIdentifier>
#          <xsl:attribute name="relatedIdentifierType">
#            <xsl:value-of select="yoda:Properties/yoda:Persistent_Identifier/yoda:Identifier_Scheme" />
#          </xsl:attribute>
#          <xsl:attribute name="relationType"><xsl:value-of select="substring-before(yoda:Relation_Type, ':')"/></xsl:attribute>
#          <xsl:value-of select="yoda:Properties/yoda:Persistent_Identifier/yoda:Identifier" />
#       </relatedIdentifier>
#     </xsl:if>
# </xsl:template>

    relatedIdentifiers = ''
    for relPackage in dict['Descriptive-group']['Related_Datapackage']:
        relType = relPackage['Relation_Type']
        #title = relPackage['Title']
        persistentSchema = relPackage['Persistent_Identifier']['Identifier_Scheme']
        persistentID = relPackage['Persistent_Identifier']['Identifier']
        relatedIdentifiers = relatedIdentifiers + '<relatedIdentifier relatedIdentifierType="' + persistentSchema + '" relationType="' + relType + '">' + persistentID + '</relatedIdentifier>'

    return '<relatedIdentifiers>' + relatedIdentifiers + '<relatedIdentifiers>'

def getGeoLocations(dict):
#        <xsl:if test="yoda:Covered_Geolocation_Place">
#          <geoLocations>
#            <xsl:apply-templates select="yoda:Covered_Geolocation_Place"/>
#          </geoLocations>
#        </xsl:if>
#
#            <xsl:template match="yoda:Covered_Geolocation_Place">
#              <geoLocation>
#                <geoLocationPlace><xsl:value-of select="." /></geoLocationPlace>
#              </geoLocation>
#            </xsl:template>
    geoLocations = '';
    locationList = dict['Descriptive-group']['Covered_Geolocation_Place']
    for location in locationList:
        geoLocations = geoLocations + '<geoLocation>' + location + '</geoLocation>'

    return '<geoLocations>' + geoLocations + '</geoLocations>'







