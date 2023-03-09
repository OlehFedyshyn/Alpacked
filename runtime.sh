#!/bin/bash

PS3="Select the runtime: "

select RUNTIME in Python NodeJS; do
    case $RUNTIME in
        Python)
            echo "Selected runtime: ${RUNTIME}"
            export RUNTIME=${RUNTIME}
            echo "Installing libs..."
            docker run --platform=linux/amd64 -t -i \
                $(pwd)/lambdas/python:/src/app \
                python:3.9-buster \
                pip3 install --upgrade -r /src/app/requirements.txt -t /src/app/layer/python
            break
            ;;
        NodeJS)
            echo "Selected runtime: ${RUNTIME}"
            export RUNTIME=${RUNTIME}
            echo "Installing libs..."
            docker run --platform=linux/amd64 -t -i \
                -v $(pwd)/lambdas/nodejs:/src/app \
                node:16-buster \
                cd /src/app && sh install-dependencies.sh
            break
            ;;
        *)
            echo "Invalid option!"
            ;;
    esac
done