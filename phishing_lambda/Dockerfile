FROM public.ecr.aws/lambda/python:3.11

ADD . /code

WORKDIR /code

RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install awslambdaric boto3

ENTRYPOINT [ "python", "-m", "awslambdaric" ]
CMD [ "main.lambda_handler" ]