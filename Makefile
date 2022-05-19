BUCKET := taxi-service-gljun2021-04
BUILD_STAMP := $(shell date +%s )

init: check-env prepare-build
	@echo "initializing workspace"
	aws s3api create-bucket --bucket $(BUCKET) --region us-east-1 --acl public-read --object-ownership BucketOwnerPreferred

	aws cloudformation deploy --template-file src/stack/base.yml --stack-name base-stack \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

build: check-env prepare-build
	@echo "running build"
	@echo "copying files to build directory"
	# upload layer zip
	mkdir /tmp/gl-build/$(BUILD_STAMP)/python
	pip3 install -r src/requirements.txt --target /tmp/gl-build/$(BUILD_STAMP)/python/
	cd /tmp/gl-build/$(BUILD_STAMP)/python/; rm -r *dist-info __pycache__
	cd /tmp/gl-build/$(BUILD_STAMP)/; zip -r /tmp/gl-build/layer.zip python;
	aws s3 cp /tmp/gl-build/layer.zip s3://$(BUCKET)/build/$(GLNAME)-$(BUILD_STAMP)-layer.zip
	# upload lambda zip
	rm -rf /tmp/gl-build/$(BUILD_STAMP)/*; cp src/lambda/* /tmp/gl-build/$(BUILD_STAMP)/
	cd /tmp/gl-build/$(BUILD_STAMP)/; zip -r /tmp/gl-build/lambda.zip *; rm -rf /tmp/gl-build/$(BUILD_STAMP);
	aws s3 sync src/ s3://$(BUCKET)/build/$(GLNAME)/$(BUILD_STAMP)/ --acl public-read
	aws s3 cp /tmp/gl-build/lambda.zip s3://$(BUCKET)/build/$(GLNAME)/$(BUILD_STAMP)/

deploy: build
	@echo "deploying application"
	aws cloudformation validate-template --template-url https://$(BUCKET).s3.amazonaws.com/build/$(GLNAME)/$(BUILD_STAMP)/stack/main.yml > /dev/null
	aws cloudformation deploy --template-file src/stack/main.yml --stack-name $(GLNAME)-taxi-service \
		--parameter-overrides Bucket=$(BUCKET) Namespace=$(GLNAME) BuildStamp=$(BUILD_STAMP)\
		DbSubnetId=subnet-02286615e3f602c96 LambdaSecurityGroup=sg-02b5c584492efd383 \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM


undeploy: check-env
	@echo "running undeploy"
	aws cloudformation delete-stack --stack-name $(GLNAME)-taxi-service

cleanup: check-env
	@echo "running cleanup"
	aws s3 rm s3://$(BUCKET)/build/$(GLNAME)/ --recursive
	rm -rf build/*

prepare-build:
	rm -rf /tmp/gl-build/*
	rm -f /tmp/gl-build/lambda.zip
	mkdir -p /tmp/gl-build/$(BUILD_STAMP)

check-env:
ifndef GLNAME
	$(error GLNAME is undefined)
endif