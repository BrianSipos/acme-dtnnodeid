cmake_minimum_required(VERSION 3.10)
project(
    draft-ietf-acme-dtnnodeid
    LANGUAGES
)

option(VALIDATE_CBOR "Run diag2cbor on fragments from the document" ON)

add_subdirectory(spec)
