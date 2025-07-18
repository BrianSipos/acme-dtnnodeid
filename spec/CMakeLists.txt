# Inherit variables from top-level project
set(DRAFT_NAME "${PROJECT_NAME}")
set(DOC_INCLUDES )

find_program(XML2RFC xml2rfc)
if(NOT XML2RFC)
    message(FATAL_ERROR "Program xml2rfc not found")
endif()
find_program(XMLSTARLET xmlstarlet)
if(NOT XMLSTARLET)
    message(FATAL_ERROR "Program xmlstarlet not found")
endif()
find_program(ASPELL aspell)
if(NOT ASPELL)
    message(FATAL_ERROR "Program aspell not found")
endif()
find_program(PYTHON python3)
if(NOT PYTHON)
    message(FATAL_ERROR "Program python3 not found")
endif()
set(SPLIT_ARTWORK "${CMAKE_CURRENT_SOURCE_DIR}/split_artwork.py")

set(DRAFT_NAME_XML "${CMAKE_CURRENT_SOURCE_DIR}/${DRAFT_NAME}.xml")
set(DRAFT_NAME_TXT "${DRAFT_NAME}.txt")
set(DRAFT_NAME_HTML "${DRAFT_NAME}.html")
set(DRAFT_NAME_PDF "${DRAFT_NAME}.pdf")
set(DRAFT_NAME_EXPAND "${DRAFT_NAME}-exp.xml")
add_custom_command(
    OUTPUT "${DRAFT_NAME_TXT}"
    DEPENDS "${DRAFT_NAME_XML}" ${DOC_INCLUDES}
    COMMAND ${XML2RFC} --no-network --text -o "${DRAFT_NAME_TXT}" "${DRAFT_NAME_XML}"
)
add_custom_command(
    OUTPUT "${DRAFT_NAME_HTML}"
    DEPENDS "${DRAFT_NAME_XML}" ${DOC_INCLUDES}
    COMMAND ${XML2RFC} --no-network --html -o "${DRAFT_NAME_HTML}" "${DRAFT_NAME_XML}"
)
add_custom_command(
    OUTPUT "${DRAFT_NAME_PDF}"
    DEPENDS "${DRAFT_NAME_XML}" ${DOC_INCLUDES}
    COMMAND ${XML2RFC} --no-network --pdf -o "${DRAFT_NAME_PDF}" "${DRAFT_NAME_XML}"
)
add_custom_command(
    OUTPUT "${DRAFT_NAME_EXPAND}"
    DEPENDS "${DRAFT_NAME_XML}" ${DOC_INCLUDES}
    COMMAND ${XML2RFC} --no-network --expand -o "${DRAFT_NAME_EXPAND}" "${DRAFT_NAME_XML}"
)
add_custom_target(
    specs ALL
    DEPENDS 
        "${DRAFT_NAME_TXT}"
        "${DRAFT_NAME_HTML}"
        "${DRAFT_NAME_EXPAND}"
)
add_custom_target(
    pdf
    DEPENDS "${DRAFT_NAME_PDF}"
)

set(DICTIONARY_TXT "${CMAKE_CURRENT_SOURCE_DIR}/dictionary.txt")
set(SPELLCHECK_XSL "${CMAKE_CURRENT_SOURCE_DIR}/spellcheck.xsl")
set(MISSPELLING_TXT "misspelling.txt")
add_custom_command(
    OUTPUT "dictionary.cwl"
    DEPENDS "${DICTIONARY_TXT}"
    COMMAND cat "${DICTIONARY_TXT}" |
        ${ASPELL} --lang=en create master "./dictionary.cwl"
)
add_custom_command(
    OUTPUT "${MISSPELLING_TXT}"
    DEPENDS "${DRAFT_NAME_XML}" "${SPELLCHECK_XSL}" "dictionary.cwl"
    COMMAND ${XMLSTARLET} tr "${SPELLCHECK_XSL}" "${DRAFT_NAME_XML}" |
        ${ASPELL} --mode=sgml --lang=EN_US --extra-dicts=./dictionary.cwl list |
        sort | uniq > "${MISSPELLING_TXT}"
)
add_custom_target(
    misspelling ALL
    DEPENDS "${MISSPELLING_TXT}"
    COMMAND cat "${MISSPELLING_TXT}"
    # success means file is present and empty
    COMMAND test -f "${MISSPELLING_TXT}" -a ! -s "${MISSPELLING_TXT}"
    COMMENT "Checking ${MISSPELLING_TXT}"
)

install(
    FILES
        "${CMAKE_CURRENT_BINARY_DIR}/${DRAFT_NAME_TXT}"
        "${CMAKE_CURRENT_BINARY_DIR}/${DRAFT_NAME_HTML}"
        "${CMAKE_CURRENT_BINARY_DIR}/${DRAFT_NAME_EXPAND}"
        "${CMAKE_CURRENT_BINARY_DIR}/${MISSPELLING_TXT}"
    TYPE DOC
)


find_program(JSONVERIFY json_verify)
if(JSONVERIFY)
    set(JSONERRORS_TXT "jsonerrors.txt")
    add_custom_command(
        OUTPUT "${JSONERRORS_TXT}"
        DEPENDS "${DRAFT_NAME_XML}" "${SPLIT_ARTWORK}"
        COMMAND ${PYTHON} "${SPLIT_ARTWORK}" "${DRAFT_NAME_XML}" '//sourcecode[@type="json"]' "${JSONVERIFY}" >/dev/null 2>"${JSONERRORS_TXT}"
    )
    add_custom_target(
        jsonerrors ALL
        DEPENDS "${JSONERRORS_TXT}"
    )
    install(
        FILES "${CMAKE_CURRENT_BINARY_DIR}/${JSONERRORS_TXT}"
        TYPE DOC
    )
endif()

# Process each CBOR fragment independently for well-formedness
find_program(CBORVERIFY diag2pretty.rb)
if(NOT CBORVERIFY)
    message(WARNING "No `diag2pretty.rb` found")
else()
    set(CBORERRORS_TXT "cborerrors.txt")
    add_custom_target(
        cborerrors ALL
        BYPRODUCTS "${CBORERRORS_TXT}"
        DEPENDS "${DRAFT_NAME_XML}" "${SPLIT_ARTWORK}"
        COMMAND ${PYTHON} "${SPLIT_ARTWORK}" --unwrap=single-bs "${DRAFT_NAME_XML}" '//sourcecode[@type="cbor"]' "${CBORVERIFY}" 2>"${CBORERRORS_TXT}" 1>&2
        COMMENT "Generating ${CBORERRORS_TXT}"
    )
    install(
        FILES "${CMAKE_CURRENT_BINARY_DIR}/${CBORERRORS_TXT}"
        TYPE DOC
    )
endif()


# Process all CDDL concatenated together
set(EXTRACTED_CDDL "extracted.cddl")
set(COMBINED_CDDL "combined.cddl")
add_custom_command(
    OUTPUT "${EXTRACTED_CDDL}"
    DEPENDS "${DRAFT_NAME_XML}"
    COMMAND ${XMLSTARLET} sel --text -t -v '//sourcecode[@type="cddl"]' "${DRAFT_NAME_XML}" >"${EXTRACTED_CDDL}"
    COMMAND sed -i "'s/[[:space:]]*$$//'" "${EXTRACTED_CDDL}"
)
add_custom_command(
    OUTPUT "${COMBINED_CDDL}"
    DEPENDS "${EXTRACTED_CDDL}"
        "${CMAKE_CURRENT_SOURCE_DIR}/../bpv7.cddl"
    COMMAND cat
        "${EXTRACTED_CDDL}"
        "${CMAKE_CURRENT_SOURCE_DIR}/../bpv7.cddl"
        >"${COMBINED_CDDL}"
)
add_custom_target(
    cddl ALL
    DEPENDS "${COMBINED_CDDL}"
)
install(
    FILES
        "${CMAKE_CURRENT_BINARY_DIR}/${EXTRACTED_CDDL}"
        "${CMAKE_CURRENT_BINARY_DIR}/${COMBINED_CDDL}"
    TYPE DOC
)
find_program(CDDLTOOL cddl)
if(NOT CDDLTOOL)
    message(WARNING "No `cddl` found")
else()
    set(CDDLERRORS_TXT "cddlerrors.txt")
    add_custom_target(
        cddlerrors ALL
        BYPRODUCTS "${CDDLERRORS_TXT}"
        DEPENDS "${COMBINED_CDDL}"
        COMMAND ${CDDLTOOL} compile-cddl --cddl "${COMBINED_CDDL}" 2>"${CDDLERRORS_TXT}" 1>&2
        COMMENT "Generating ${CDDLERRORS_TXT}"
    )
    install(
        FILES "${CMAKE_CURRENT_BINARY_DIR}/${CDDLERRORS_TXT}"
        TYPE DOC
    )

    # Check validity against CDDL for each chunk
    find_program(DIAG2CBOR diag2cbor.rb)
    if(NOT DIAG2CBOR)
        message(WARNING "No `diag2cbor.rb` found")
    elseif(VALIDATE_CBOR)
        set(CBORVALIDERRORS_TXT "cborvaliderrors.txt")
        set(CHECK_CBOR "${CMAKE_CURRENT_SOURCE_DIR}/check_cbor.sh")
        add_custom_target(
            cborvaliderrors ALL
            BYPRODUCTS "${CBORVALIDERRORS_TXT}"
            DEPENDS "${DRAFT_NAME_XML}" "${SPLIT_ARTWORK}" "${CHECK_CBOR}" "${COMBINED_CDDL}"
            COMMAND ${PYTHON} "${SPLIT_ARTWORK}" --unwrap=single-bs "${DRAFT_NAME_XML}" '//sourcecode[@type="cbor"]' "${CHECK_CBOR}" "${COMBINED_CDDL}" 2>"${CBORVALIDERRORS_TXT}" 1>&2
            COMMENT "Generating ${CBORVALIDERRORS_TXT}"
        )
        install(
            FILES "${CMAKE_CURRENT_BINARY_DIR}/${CBORVALIDERRORS_TXT}"
            TYPE DOC
        )
    endif()
endif()
