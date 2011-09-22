#!/bin/sh

# BASE_URL="http://localhost:8080"
BASE_URL="http://gaedoodler.appspot.com"

testcase () {
    command="curl -s -d uid=$2&data=$3 $BASE_URL/$1"
    /bin/echo -n $command "=> "

    result=`$command`
    echo $result

    if [ "$4" != "$result" ]; then
        echo "Assertion failed."
        exit 0
    fi
}

testcase quit test1 none ok
testcase quit test2 none ok

testcase match test1 none ok
testcase match test2 none ok

testcase mate test1 none test2
testcase mate test2 none test1

testcase update test1 abc ok
testcase update test2 xyz ok

sleep 3

testcase stroke test1 none abc
testcase stroke test2 none xyz

sleep 60

testcase stroke test1 none invalid
testcase stroke test2 none invalid

exit

testcase quit test1 none ok
testcase quit test2 none ok

testcase mate test1 none invalid
testcase mate test2 none invalid

testcase match test1 none ok
testcase match test2 none ok

testcase mate test1 none test2
testcase mate test2 none test1

testcase update test1 abc ok
testcase update test2 xyz ok

testcase stroke test1 none abc
testcase stroke test2 none xyz

testcase update test1 123 ok
testcase update test2 456 ok

testcase stroke test1 none 123
testcase stroke test2 none 456

testcase update test1 1 ok
testcase update test1 2 ok
testcase update test1 3 ok
testcase update test2 4 ok
testcase update test2 5 ok
testcase update test2 6 ok

testcase stroke test1 none 3
testcase stroke test2 none 6

testcase quit test1 none ok
testcase mate test1 none invalid
testcase mate test2 none test1

testcase quit test2 none ok
testcase mate test2 none invalid

echo "Successfully ended."
