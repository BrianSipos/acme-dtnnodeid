cmake_minimum_required(VERSION 3.10)
project(
    draft-sipos-acme-dtnnodeid
    LANGUAGES
)

set(DRAFT_NAME "${PROJECT_NAME}")

find_program(XML2RFC xml2rfc)
if(XML2RFC_NOTFOUND)
    message(FATAL_ERROR "Program xml2rfc not found")
endif()

set(DRAFT_NAME_XML "${CMAKE_CURRENT_SOURCE_DIR}/${DRAFT_NAME}.xml")
set(DRAFT_NAME_TXT "${DRAFT_NAME}.txt")
set(DRAFT_NAME_HTML "${DRAFT_NAME}.html")
add_custom_command(
    OUTPUT "${DRAFT_NAME_TXT}"
    DEPENDS "${DRAFT_NAME_XML}"
    COMMAND "${XML2RFC}" -o "${DRAFT_NAME_TXT}" "${DRAFT_NAME_XML}"
)
add_custom_command(
    OUTPUT "${DRAFT_NAME_HTML}"
    DEPENDS "${DRAFT_NAME_XML}"
    COMMAND "${XML2RFC}" --html -o "${DRAFT_NAME_HTML}" "${DRAFT_NAME_XML}"
)

find_program(ASPELL aspell)
if(ASPELL_NOTFOUND)
    message(FATAL_ERROR "Program aspell not found")
endif()

set(DICTIONARY_TXT "${CMAKE_CURRENT_SOURCE_DIR}/dictionary.txt")
set(MISSPELLING_TXT "misspelling.txt")
add_custom_command(
    OUTPUT "dictionary.cwl"
    DEPENDS "${DICTIONARY_TXT}"
    COMMAND cat "${DICTIONARY_TXT}" | 
        ${ASPELL} --lang=en create master "./dictionary.cwl"
)
add_custom_command(
    OUTPUT "${MISSPELLING_TXT}"
    DEPENDS "${DRAFT_NAME_XML}" "dictionary.cwl"
    COMMAND cat "${DRAFT_NAME_XML}" | 
        ${ASPELL} --mode=sgml --lang=EN_US --extra-dicts=./dictionary.cwl list | 
        sort | uniq > "${MISSPELLING_TXT}"
)

find_program(XMLSTARLET xmlstarlet)
if(XMLSTARLET_NOTFOUND)
    message(FATAL_ERROR "Program xmlstarlet not found")
endif()
find_program(JSONVERIFY json_verify)
if(JSONVERIFY_NOTFOUND)
    message(FATAL_ERROR "Program json_verify not found")
endif()
set(JSONERRORS_TXT "jsonerrors.txt")
add_custom_command(
    OUTPUT "${JSONERRORS_TXT}"
    DEPENDS "${DRAFT_NAME_XML}"
    COMMAND cat "${DRAFT_NAME_XML}" | 
        ${XMLSTARLET} sel --text -t -v "//artwork[@type=\\\"application/json\\\"]" - |
        ${JSONVERIFY} -s 2> "${JSONERRORS_TXT}" || true
)

add_custom_target(
    specs ALL
    DEPENDS "${DRAFT_NAME_TXT}" "${DRAFT_NAME_HTML}" "${MISSPELLING_TXT}" "${JSONERRORS_TXT}"
)
