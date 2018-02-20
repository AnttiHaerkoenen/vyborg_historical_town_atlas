pushd %~dp0
rem md docs
    move docs html
    cd html

    make html
    cd ..

    move html docs

popd
pause