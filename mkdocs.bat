pushd %~dp0
rem md docs
    move docs html
    cd html

    call make.bat html
    cd ..

    move html docs

popd
pause