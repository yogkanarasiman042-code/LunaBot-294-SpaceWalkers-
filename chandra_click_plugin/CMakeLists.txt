cmake_minimum_required(VERSION 3.10)

project(chandra_click_plugin)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core Quick)
find_package(gz-gui REQUIRED)
find_package(gz-rendering REQUIRED)

qt_add_resources(CHANDRA_QRC
    ChandraClickGoal.qrc
)

add_library(ChandraClickGoal SHARED
    src/ChandraClickGoal.cc
    ${CHANDRA_QRC}
)

target_link_libraries(ChandraClickGoal
    PRIVATE
    Qt6::Core
    Qt6::Quick
    gz-gui::gz-gui
    gz-rendering::gz-rendering
)
