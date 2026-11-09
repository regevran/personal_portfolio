cmake_minimum_required(VERSION 3.25)

project(personal_portfolio VERSION 0.1.0 LANGUAGES NONE)

find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter)
find_program(PANDOC_EXECUTABLE pandoc REQUIRED)

enable_testing()

# Repository layout. The site is generated into dist/ in the source tree, so
# the output can be inspected or copied without leaving the build system. The
# build/ tree is disposable and holds the build stamp and test output.
set(PORTFOLIO_ROOT  "${CMAKE_CURRENT_SOURCE_DIR}")
set(PORTFOLIO_BUILD "${CMAKE_BINARY_DIR}")
set(PORTFOLIO_DIST  "${PORTFOLIO_ROOT}/dist")
set(PORTFOLIO_STAMP "${PORTFOLIO_BUILD}/site.stamp")

set(PORTFOLIO_SERVE_PORT 8000 CACHE STRING "Port for the preview server")

message(STATUS "portfolio: Python       ${Python3_EXECUTABLE}")
message(STATUS "portfolio: Pandoc       ${PANDOC_EXECUTABLE}")
message(STATUS "portfolio: build tree   ${PORTFOLIO_BUILD}")
message(STATUS "portfolio: output       ${PORTFOLIO_DIST}")

# Every source file that can change the rendered site. CONFIGURE_DEPENDS makes
# the build re-glob after files are added or removed.
file(GLOB_RECURSE PORTFOLIO_INPUTS CONFIGURE_DEPENDS
    "${PORTFOLIO_ROOT}/content/*"
    "${PORTFOLIO_ROOT}/templates/*"
    "${PORTFOLIO_ROOT}/assets/*")
list(APPEND PORTFOLIO_INPUTS
    "${PORTFOLIO_ROOT}/src/__init__.py"
    "${PORTFOLIO_ROOT}/src/build.py"
    "${PORTFOLIO_ROOT}/src/site_schema.py"
    "${PORTFOLIO_ROOT}/tests/test_content.py"
    "${PORTFOLIO_ROOT}/tests/warnings.py"
    "${PORTFOLIO_ROOT}/tests/validate.py")

# The renderer owns dist/: it clears the directory and writes every page. A
# stamp in the build tree records that a successful render is up to date, so
# an unchanged tree skips the render and a failed render never leaves a stale
# stamp behind.
add_custom_command(
    OUTPUT  "${PORTFOLIO_STAMP}"
    COMMAND "${Python3_EXECUTABLE}" -m unittest -q tests.test_content
    COMMAND "${Python3_EXECUTABLE}" -m tests.warnings
    COMMAND "${Python3_EXECUTABLE}" -m src.build
    COMMAND "${CMAKE_COMMAND}" -E touch "${PORTFOLIO_STAMP}"
    DEPENDS ${PORTFOLIO_INPUTS}
    WORKING_DIRECTORY "${PORTFOLIO_ROOT}"
    COMMENT "Rendering the site into dist/"
    VERBATIM)

add_custom_target(site-build ALL
    DEPENDS "${PORTFOLIO_STAMP}")

# Network access is explicit, matching the birds data pipeline: the default
# build is offline and uses the cached dates in content/data/repos.json.
add_custom_target(site-refresh-repos
    COMMAND "${Python3_EXECUTABLE}" -m src.fetch_repos
    WORKING_DIRECTORY "${PORTFOLIO_ROOT}"
    COMMENT "Refreshing repository last-push dates from GitHub"
    USES_TERMINAL
    VERBATIM)

add_custom_target(site-serve
    COMMAND "${Python3_EXECUTABLE}" -m http.server -d "${PORTFOLIO_DIST}"
            "${PORTFOLIO_SERVE_PORT}"
    DEPENDS site-build
    COMMENT "Serving dist/ at http://localhost:${PORTFOLIO_SERVE_PORT}"
    USES_TERMINAL
    VERBATIM)

# Two validation passes bracket the build: content before, output after. The
# workflow presets build first, so ctest always sees a fresh dist/. The
# non-fatal date warnings print during the render.
add_test(NAME content-validation
    COMMAND "${Python3_EXECUTABLE}" -m unittest -q tests.test_content)
add_test(NAME output-validation
    COMMAND "${Python3_EXECUTABLE}" -m unittest -q tests.test_output)

set_tests_properties(content-validation output-validation
    PROPERTIES WORKING_DIRECTORY "${PORTFOLIO_ROOT}")
set_tests_properties(output-validation
    PROPERTIES DEPENDS "content-validation")

add_custom_target(site-test
    COMMAND "${CMAKE_CTEST_COMMAND}" --output-on-failure
    DEPENDS site-build
    WORKING_DIRECTORY "${PORTFOLIO_BUILD}"
    USES_TERMINAL
    VERBATIM)

# A clean build also removes the generated site from the source tree.
set_property(DIRECTORY APPEND PROPERTY ADDITIONAL_CLEAN_FILES
    "${PORTFOLIO_DIST}")

# Deploy foundation: stage the generated site with
#   cmake --install build --prefix <destination>
# The actual host and upload step are still deferred.
install(DIRECTORY "${PORTFOLIO_DIST}/" DESTINATION "."
        COMPONENT site)

add_custom_target(usage
    COMMAND ${CMAKE_COMMAND} -E echo "Configure:     cmake --preset default"
    COMMAND ${CMAKE_COMMAND} -E echo "Build:         cmake --build --preset default"
    COMMAND ${CMAKE_COMMAND} -E echo "Build + test:  cmake --workflow --preset site"
    COMMAND ${CMAKE_COMMAND} -E echo "Refresh dates: cmake --workflow --preset refresh"
    COMMAND ${CMAKE_COMMAND} -E echo "Test:          ctest --preset default"
    COMMAND ${CMAKE_COMMAND} -E echo "Serve:         cmake --build --preset serve"
    COMMAND ${CMAKE_COMMAND} -E echo "Stage deploy:  cmake --install build --prefix <dir>"
    COMMAND ${CMAKE_COMMAND} -E echo "Clean:         cmake --build build --target clean"
    VERBATIM)
