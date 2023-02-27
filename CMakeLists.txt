cmake_minimum_required(VERSION 3.18)

set(embed_resources_dir
    ${CMAKE_CURRENT_LIST_DIR}
    CACHE INTERNAL "")

project(embed_resources VERSION 0.1.0)

function(embed_resources targetname)

  cmake_parse_arguments(PARSE_ARGV 1 PARSED_ARGS "" "NAMESPACE;TRIM" "FILES")

  if(PARSED_ARGS_UNPARSED_ARGUMENTS)
    message(FATAL_ERROR "unknown argument ${PARSED_ARGS_UNPARSED_ARGUMENTS}")
  endif()

  if(NOT PARSED_ARGS_NAMESPACE)
    message(FATAL_ERROR "embed_resources needs NAMESPACE")
  endif()

  if(NOT PARSED_ARGS_TRIM)
    set(PARSED_ARGS_TRIM)
  endif()

  if(NOT PARSED_ARGS_FILES)
    message(FATAL_ERROR "embed_resources needs FILES")
  endif()

  set(include_dir
      ${CMAKE_CURRENT_BINARY_DIR}/embed_resources_generated)
  set(out_dir ${include_dir}/embed_resources/${PARSED_ARGS_NAMESPACE})

  file(MAKE_DIRECTORY ${out_dir})

  find_package(PythonInterp 3 REQUIRED)

  set(out_file_names)
  set(out_files)
  foreach(infile ${PARSED_ARGS_FILES})
    string(REPLACE ${PARSED_ARGS_TRIM} "" outfile ${infile})
    string(MAKE_C_IDENTIFIER ${outfile} tmp_variable_name)
    string(SUBSTRING ${tmp_variable_name} 1 -1 variable_name)
    string(SUBSTRING ${outfile} 1 -1 name_only_file)
    string(APPEND outfile ".cpp")
    list(APPEND out_file_names ${name_only_file})
    string(PREPEND outfile ${out_dir})
    list(APPEND out_files ${outfile})

    add_custom_command(
      OUTPUT ${outfile}
      COMMAND
        "${PYTHON_EXECUTABLE}" "${embed_resources_dir}/tools/genResource.py"
        --input ${infile} --output ${outfile} --namespace
        ${PARSED_ARGS_NAMESPACE} --name ${variable_name}
      COMMENT "Generating resource from ${infile}"
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      DEPENDS "${embed_resources_dir}/tools/genResource.py" ${infile})

  endforeach()

  add_custom_command(
    OUTPUT ${out_dir}/lookup.hpp
    OUTPUT ${out_dir}/lookup.cpp
    COMMAND
      "${PYTHON_EXECUTABLE}" "${embed_resources_dir}/tools/genLookup.py"
      --output "${out_dir}/lookup" --namespace
      ${PARSED_ARGS_NAMESPACE} --input ${out_file_names}
    COMMENT "Generating resource lookup ${PARSED_ARGS_NAMESPACE}"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS "${embed_resources_dir}/tools/genLookup.py" ${out_files})

  add_library(${targetname} ${out_files} "${out_dir}/lookup.cpp")
  target_include_directories(${targetname} PUBLIC ${include_dir})

endfunction()
