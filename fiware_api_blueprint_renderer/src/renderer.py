#!/usr/bin/env python

import inspect
import json
import os
import re
import shutil
from subprocess import call
import sys

from jinja2 import Environment, FileSystemLoader
import markdown
import pypandoc
    


def print_api_spec_title_to_extra_file( inputFilePath, extraSectionsFilePath ):
    """Extracts the title of the API specification and writes it to the extra sections file

    Arguments:
    inputFilePath -- File with the API specification
    extraSectionsFilePath -- File where we will write the extra sections
    """
    with open( inputFilePath, 'r' ) as inputFilePath, open( extraSectionsFilePath, 'w') as extraSectionsFile:
        line = inputFilePath.readline()
        while( line != "" and not line.startswith( "# " ) ):
            line = inputFilePath.readline()
    
        extraSectionsFile.write( line )


def separate_extra_sections_and_api_blueprint( inputFilePath, extraSectionsFilePath, APIBlueprintFilePath ):
    """Divides a Fiware API specification into extra sections and its API blueprint.

    Arguments:
    inputFilePath -- A Fiware API specification file.
    extraSectionsFilePath -- Resulting file containing extra information about the API specification.
    APIBlueprintFilePath -- Resulting file containing the API blueprint of the Fiware API.
    """
    print_api_spec_title_to_extra_file( inputFilePath, extraSectionsFilePath )
   
    with open( inputFilePath, 'r' ) as inputFilePath, open( extraSectionsFilePath, 'a') as extraSectionsFile, open( APIBlueprintFilePath, 'w' ) as APIBlueprintFile:
        copy = False
        for line in inputFilePath:
            if line.strip() == "## Editors":
                copy = True
            elif line.strip() == "## Data Structures":
                copy = False

            if copy:
                extraSectionsFile.write( line )
            else:
                APIBlueprintFile.write( line )


def parser_api_blueprint( APIBlueprintFilePath, APIBlueprintJSONFilePath ):
    """Extracts from API Blueprint file the API specification and saves it to a JSON file

    Arguments:
    APIBlueprintFilePath -- An API Blueprint definition file 
    APIBlueprintJSONFilePath -- Path to JSON file
    """

    call( ["drafter", APIBlueprintFilePath, "--output", APIBlueprintJSONFilePath, "--format", "json", "--use-line-num"] )


def get_markdow_title_id( sectionTitle ):
    """Returns the HTML equivalent id from a section title
    
    Arguments: 
    sectionTitle -- Section title
    """
    return sectionTitle.replace( " ", "_" ).lower()


def get_heading_level( heading ):
    """Returns the level of a given Markdown heading
    
    Arguments:
    heading -- Markdown title    
    """
    i = 0
    while( i < len( heading ) and heading[i] == '#' ):
        i += 1

    return i


def create_json_section( sectionMarkdownTitle, sectionBody ):
    """Creates a JSON
    
    Arguments:
    sectionMarkdownTitle -- Markdown title of the section
    sectionBody -- body of the subsection
    """
    sectionTitle = sectionMarkdownTitle.lstrip( '#' ).strip()

    section = {}
    section["id"] = get_markdow_title_id( sectionTitle )
    section["name"] = sectionTitle
    section["body"] = markdown.markdown( sectionBody.decode('utf-8'), extensions=['markdown.extensions.tables'] )
    section["subsections"] = []

    return section


def get_subsection_body( fileDescriptor ):
    body=''
    line = fileDescriptor.readline()

    while line and not line.startswith('#'):
        body += line
        line = fileDescriptor.readline()

    return (body, line)


def parse_metadata_subsections( fileDescriptor, parentSectionJSON, lastReadLine=None ):
    """Generates a JSON tree of nested metadata sections

    Arguments:
    fileDescriptor -- list of lines with the content of the file
    parentSectionJSON -- JSON object representing the current parent section
    lastReadLine -- Last remaining read line 
    """
    
    if lastReadLine is None:
        line = fileDescriptor.readline()
    else:
        line = lastReadLine

    # EOF case
    if not line:
        return line

    if( line.startswith( '#' ) ):
        sectionName = line
        ( body , line ) = get_subsection_body( fileDescriptor )

        sectionJSON = create_json_section( sectionName, body )

        parentSectionJSON['subsections'].append(sectionJSON)

        sectionLevel = get_heading_level( sectionName )
        nextSectionLevel = get_heading_level( line )

        if sectionLevel == nextSectionLevel:   # Section sibling
           nextLine = parse_metadata_subsections( fileDescriptor, parentSectionJSON, lastReadLine=line ) 
        elif sectionLevel < nextSectionLevel:  # Section child
           nextLine = parse_metadata_subsections( fileDescriptor, sectionJSON, lastReadLine=line ) 
        else:   # Not related to current section
            return line

        if not nextLine :
            return nextLine
        else:
            nextSectionLevel = get_heading_level( nextLine )

            if sectionLevel == nextSectionLevel:   # Section sibling
               nextLine = parse_metadata_subsections( fileDescriptor, parentSectionJSON, lastReadLine=nextLine ) 
            else:   # Not related to current section
                return nextLine


def parse_meta_data( filePath ):
    """Parses API metadata and returns the result in a JSON object
    
    Arguments: 
    filePath -- File with extra sections
    """
    metadata = create_json_section( "root", "" )
  
    with open( filePath, 'r' ) as file_:
        more = parse_metadata_subsections( file_, metadata )
        while more:
            more = parse_metadata_subsections( file_, metadata, more )

    return metadata


def add_metadata_to_json( metadata, jsonFilePath ):
    """Adds metadata values to a json file
    
    Arguments: 
    metadata -- Metadata values in JSON format
    jsonFilePath -- Path to JSON file
    """

    jsonContent = ""

    with open( jsonFilePath, 'r' ) as jsonFile:
        jsonContent = json.load( jsonFile )
        jsonContent['api_metadata'] = {}
        for metadataKey in metadata:
            jsonContent['api_metadata'][metadataKey] = metadata[metadataKey]

    with open( jsonFilePath, 'w' ) as jsonFile:
        json.dump( jsonContent, jsonFile, indent=4 )


def parser_json_descriptions_markdown( jsonFilePath ):
    """Gets the descriptions of the resources and parses them as markdown. Saves the result in the same JSON file.
    
    Arguments: 
    jsonFilePath -- Path to JSON file
    """
    jsonContent = ""
    
    with open( jsonFilePath, 'r' ) as jsonFile:
        jsonContent = json.load( jsonFile )
        for resourceGroup in jsonContent['resourceGroups']:
            for resource in resourceGroup['resources']:
                resource['description'] = markdown.markdown( resource['description'], extensions=['markdown.extensions.tables'] )
    
    with open( jsonFilePath, 'w' ) as jsonFile:
        json.dump( jsonContent, jsonFile, indent=4 )

def copy_static_files( templateDirPath, dstDirPath ):


    if os.path.exists(dstDirPath+"/css"):
        shutil.rmtree(dstDirPath+"/css")
    shutil.copytree(templateDirPath+"/css", dstDirPath+"/css")

    if os.path.exists(dstDirPath+"/js"):
        shutil.rmtree(dstDirPath+"/js")
    shutil.copytree(templateDirPath+"/js", dstDirPath+"/js")




def render_api_blueprint( templateFilePath, contextFilePath, dstDirPath ):
    """Renders an API Blueprint context file with a Jinja2 template.
    
    Arguments: 
    templateFilePath -- The Jinja2 template path 
    contextFilePath -- Path to the context file  
    dstDirPath -- Path to save the compiled site
    """

    env = Environment( loader=FileSystemLoader( os.path.dirname( templateFilePath ) ) )
    template = env.get_template( os.path.basename( templateFilePath ) )
    output = ""
    with open( contextFilePath, "r" ) as contextFile:
        output = template.render( json.load( contextFile ) )

    renderedHTMLFilename = os.path.splitext( os.path.basename( contextFilePath ) )[0]
    renderedHTMLPath = os.path.join( dstDirPath, renderedHTMLFilename + ".html" )
    with open( renderedHTMLPath, "w" ) as outputFile:
        outputFile.write( output.encode('utf-8') )

    copy_static_files( os.path.dirname(templateFilePath), dstDirPath )


def create_directory_if_not_exists( dirPath ):
    """Creates a directory with the given path if it doesn't exists yet"""

    if not os.path.exists( dirPath ):
        os.makedirs( dirPath )


def clear_directory( dirPath ):
    """Removes all the files on a directory given its path"""
    
    for file in os.listdir( dirPath ):
        filePath = os.path.join( dirPath, file )
        try:
            if os.path.isfile( filePath ):
                os.unlink( filePath )
        except Exception, e:
            print e

def parse_property_member_declaration( property_member_declaration_string ):
  """ Utility to parse the declaration of a property member into custom JSON. Based on the MSON specification. """
  

  # Store MSON reserved words for the parsing below.
  # We are interested in the type attribute reserved keywords in order to know whether 
  # a property member is required or optional.
  reserved_keywords = {}
  reserved_keywords['type_attribute'] = [ 'required', 'optional', 'fixed', 'sample', 'default' ]

  if property_member_declaration_string == '': return {}

  # We first parse the line in order to get the following fields:
  #  - property_name: The name given to the property
  #  - type_definition_list: The list with the technical definition of the property. Since this
  #    list is unordered, we will parse it later to find the needed keywords.
  #  - description: The text provided to describe the context of the property.
  regex_string = "^[ ]*[-|+][ ](?P<property_name>\w+)[ ]*(?:[[: ][\w, ]*]?[ ]*\((?P<type_definition_list>[\w\W ]+)\))?[ ]*(?:[-](?P<property_description>[ \w\W]+))?\Z"
  declaration_regex = re.compile(regex_string)

  declaration_match = declaration_regex.match( property_member_declaration_string )
  declaration_dict = declaration_match.groupdict()
  
  property_declaration={}
  property_declaration['name'] = declaration_dict['property_name']
  property_declaration['description'] = declaration_dict['property_description']

  # We construct the type_definition field from the type_definition_list field retrieved in the
  # regular expression.
  property_declaration['required']=False      # Default value for the required attribute
  for type_specification_attribute in declaration_dict['type_definition_list'].split(','):
    # If the current element is not in the type_attributes reserved keywords list, it is
    # the property type specification.
    if type_specification_attribute.strip() not in reserved_keywords['type_attribute']:
      property_declaration['type'] = type_specification_attribute.strip()
    else:
      if type_specification_attribute.strip() == 'required': property_declaration['required']=True

  return property_declaration

def parse_defined_data_structures( data ):
  """Retrieves data structures definition from JSON fragment and gives them back as Python dict"""
  data_structure_dict = {}

  try:
    if data["content"][0]["sections"][0]["class"] != u'blockDescription':
        raise ValueError('Unexpected section received.')
  except:
    return data_structure_dict


  for content in data["content"]:
    data_structure = {}
    data_structure_definition = []

    if content["sections"]!=[]:
      data_structure_content = content["sections"][0]["content"]

      for property_member_declaration in data_structure_content.split('\n'):
        if property_member_declaration != '':

          parsed_attribute_definition = parse_property_member_declaration( property_member_declaration )
          data_structure_definition.append(parsed_attribute_definition)

    data_structure_name = content["name"]["literal"]
    data_structure["attributes"] = data_structure_definition
    data_structure_dict[data_structure_name] = data_structure

  return data_structure_dict

def parser_json_data_structures( jsonFilePath ):
    """Retrieves data structures definition from JSON file and writes them in an easier to access format"""
    
    jsonContent = ""

    with open( jsonFilePath, 'r' ) as jsonFile:
        jsonContent = json.load( jsonFile )

    #jsonContent['data_structures'] = parse_defined_data_structures( jsonContent['content'][0] )
    
    with open( jsonFilePath, 'w' ) as jsonFile:
        json.dump( jsonContent, jsonFile, indent=4 )


def render_api_specification( APISpecificationPath, templatePath, dstDirPath, clearTemporalDir = True ):
    """Renders an API specification using a template and saves it to destination directory.
    
    Arguments: 
    APISpecificationPath -- Path to API Blueprint specification
    templatePath -- The Jinja2 template path
    dstDirPath -- Path to save the compiled site
    clearTemporalDir -- Flag to clear temporary files generated by the script  
    """

    tempDirPath = "/var/tmp/fiware_api_blueprint_renderer_tmp"

    APISpecificationFileName = os.path.splitext( os.path.basename( APISpecificationPath ) )[0]

    APIExtraSectionsFilePath = os.path.join( tempDirPath, APISpecificationFileName + '.extras' )
    APIBlueprintFilePath = os.path.join( tempDirPath + '/' + APISpecificationFileName + '.apib' )
    APIBlueprintJSONFilePath = os.path.join( tempDirPath + '/' + APISpecificationFileName + '.json' )
    
    create_directory_if_not_exists( tempDirPath )
    separate_extra_sections_and_api_blueprint( APISpecificationPath, APIExtraSectionsFilePath, APIBlueprintFilePath )
    parser_api_blueprint( APIBlueprintFilePath, APIBlueprintJSONFilePath )
    add_metadata_to_json( parse_meta_data( APIExtraSectionsFilePath ), APIBlueprintJSONFilePath )
    parser_json_descriptions_markdown( APIBlueprintJSONFilePath )
    parser_json_data_structures( APIBlueprintJSONFilePath )
    render_api_blueprint( templatePath, APIBlueprintJSONFilePath, dstDirPath )
    if( clearTemporalDir == True ):
        clear_directory( tempDirPath )


def main():   
    
    if( len( sys.argv ) < 3 or len( sys.argv ) > 4 ):
        print "ERROR: This script expects 2 / 3 arguments"
        print "Usage: \n\t" + sys.argv[0] + " <api-spec-path> <dst-dir> [clear-temp-dir]"
        sys.exit(-1)

    default_theme = os.path.dirname(__file__)+"/../themes/default_theme/api-specification.tpl"

    create_directory_if_not_exists( sys.argv[2] )

    render_api_specification( sys.argv[1], default_theme, sys.argv[2], ( len( sys.argv ) != 4 or ( sys.argv[3] ) ) )
    sys.exit(0)


if __name__ == "__main__":
    main()
