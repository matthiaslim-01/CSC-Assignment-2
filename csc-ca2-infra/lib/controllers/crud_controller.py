# boto3 for connection to S3.
import boto3
from botocore.exceptions import ClientError
# logging for logging.
import logging
# uuid for creating Universally Unique IDs.
import uuid
# imghdr for image validation.
import imghdr
# pymysql for mySql connection.
import pymysql
# PIL Image for opening image files.
from PIL import Image
# base64 for base 64 encoding/decoding.
import base64
# io for dealing with file objects with different I/O.
import io
# lib.webexception for raising web exception when an error occurs.
from lib.webexception import WebException
# http for usage of HttpStatusCodes.
from http import HTTPStatus
# google.cloud for the usage of Cloud Vision to detect faces.
from google.cloud import vision
# os for usage of envionment variables.
import os

"""
TODO
Validations before upload
    File must be an image file
    Image must contain human face

POST method (Create)
    Send image file to S3 bucket
    Send link, talent_name and talent_description to mySql.

PUT method (Update)
    Note: image, talent_name and talent_description can be changed.
        Make sure whether changing image will change the URL.
    Basically, strip Upload method and reassemble to fit.

GET method (Read)
    GET all
        Retrieve all values from mySql.
    GET by related search terms
        Search function to sift through via related terms in talent_name and talent_description.

DELETE method (Delete)
    Delete said talent's image in S3 bucket, image link, talent_name and talent_description in mySql.
"""

def init_client(): 
    try:
        return boto3.client('s3', region_name='us-east-1')
    except ClientError as e:
        logging.error("init_client -- %s", e)
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e

def isValidImageFile(file):
    fileType = imghdr.what(file)
    if (fileType == "jpeg" or fileType == "png"):
        logging.info(
            "isValidImageFile -- File Validation for Image: Passed")
        return True
    else:
        logging.error(
            "isValidImageFile -- File Validation for Image: Failed")
        return False

def containsHumanFace(base64, img):
    # Check if file is an Image
    if (isValidImageFile(img)):
        # Check if Image contains Human face by using Cloud Vision API
        client = vision.ImageAnnotationClient()
        # Set confidence level after done.
        content = base64.read()
        image = vision.Image(content=content)
        CVResponse = client.face_detection(image=image)
        faces = CVResponse.face_annotations
        confidence = int(faces.detectionConfidence)

        if (confidence >= 0.7):
            logging.info(
                "containsHumanFace -- Image contains Human Face: Passed")
            return True
        else:
            logging.error(
                "containsHumanFace -- Image contains Human Face: Failed")
            return False
    else:
        return False

def uploadToSql(query):
    # Connection to mySql server
    connection = pymysql.connect(host=os.environ["HOST"], user=os.environ["USER"], password=os.environ["PASSWORD"], database=os.environ["DATABASE"])
    logging.info("uploadToSql -- Connection to mySql server successful!")

    try:
        cur = connection.cursor()
        cur.execute(query)
        logging.info("uploadToSql -- Insert query executed.")

    except ClientError as e:
        logging.error(e)
        return False

    finally:
        logging.info("uploadToSql -- Closing mySql connection")
        connection.close()

    return True

def getUUID(URL):
    # Get UUID of target Talent for deletion
    splicedUUID = URL.split("/")[-1]
    logging.info("getUUID -- Target UUID: %s", splicedUUID)
    return splicedUUID

def uploadImage(request, response):
    # Load file
    data = request.data
    file = data["inputFiles"]
    image = base64.b64decode(str(file))
    img = Image.open(io.BytesIO(image))

    # Validations
    if (containsHumanFace(file, img) == False):
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message="uploadImage -- File failed Validations.")

    # Setting UUID for this file
    objectKey = str(uuid.uuid4())
    logging.info("uploadImage -- New UUID: %s", objectKey)

    # Setting other values
    talent_name = data["talentName"]
    talent_bio = data["talentBio"]
    # UPDATE THIS 2 VARIABLES TO NOT BE HARDCODED
    bucketName = "csc-ca2-crud-test-bucket"
    bucketRegion = "us-east-1"

    try:
        # Uploading file to S3
        s3Response = init_client().upload_fileobj(img, bucketName, objectKey)
        logging.info("uploadImage -- S3 Upload response: %s", s3Response)

        # Set the s3 URL to current Image
        URL = "https://" + bucketName + ".s3." + bucketRegion + ".amazonaws.com/" + objectKey

        # Upload to mySql table
        insertQuery = "INSERT INTO talent (UrlLink, Name, Bio) VALUES (%s, %s, %s)", (URL, talent_name, talent_bio)
        uploadToSql(insertQuery)

    except ClientError as e:
        logging.error("uploadImage -- %s", e)
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e

    return response

def updateTalentImage(request, response):
    data = request.data
    file = data["inputFiles"]
    image = base64.b64decode(str(file))
    img = Image.open(io.BytesIO(image))
    URL = data["url"]
    targetKey = getUUID(URL)

    # Setting other values
    talent_name = data["talentName"]
    talent_bio = data["talentBio"]
    # UPDATE THIS 2 VARIABLES TO NOT BE HARDCODED
    bucketName = "csc-ca2-crud-test-bucket"
    bucketRegion = "us-east-1"

    try:
        s3Response = init_client().upload_fileobj(img, bucketName, targetKey)
        logging.info("updateTalentImage -- S3 Update response: %s", s3Response)

        # Set the s3 URL to current Image
        URL = "https://" + bucketName + ".s3." + bucketRegion + ".amazonaws.com/" + targetKey

        # Update mySql table
        updateQuery = "UPDATE talent SET UrlLink='%s', Name='%s', Bio='%s' WHERE UrlLink LIKE '%s'", (URL, talent_name, talent_bio, targetKey)
        uploadToSql(updateQuery)

    except ClientError as e:
        logging.error("updateTalentImage -- %s", e)
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e

    return response

def deleteTalent(request, response):
    data = request.data
    URL = data["url"]
    targetKey = getUUID(URL)

    # UPDATE THIS VARIABLE TO NOT BE HARDCODED
    bucketName = "csc-ca2-crud-test-bucket"

    try:
        s3Response = init_client().delete_object(bucketName, targetKey)
        logging.info("deleteTalent -- S3 Delete response: %s", s3Response)
        
        # Delete mySql table
        deleteQuery = "DELETE FROM talents WHERE UrlLink LIKE '%s'", (targetKey)
        uploadToSql(deleteQuery)

    except ClientError as e:
        logging.error("deleteTalent -- %s", e)
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e

    return response