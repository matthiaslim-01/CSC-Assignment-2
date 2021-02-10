import pymysql
import os
from datetime import datetime
from lib.webexception import WebException
from http import HTTPStatus


def get_talent_detail(request, response):
    data = request.data

    connection = pymysql.connect(
        host=os.environ["RDS_HOST"],
        user=os.environ["RDS_USER"],
        password=os.environ["RDS_PASSWORD"],
        database=os.environ["RDS_DATABASE"],
    )

    try:
        with connection:
            getTalentData = f"Select * from talent where TalentId = {data['talentId']}"
            cur = connection.cursor(pymysql.cursors.DictCursor)
            cur.execute(getTalentData)
            talentResult = cur.fetchall()

            result = talentResult[0]

            talentDict = {
                "urlLink": result["UrlLink"],
                "name": result["Name"],
                "bio": result["Bio"],
            }
            response.body = talentDict
            cur.close()
            return response

    except Exception as e:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e


def get_comments(request, response):
    data = request.data

    commentList = []
    connection = pymysql.connect(
        host=os.environ["RDS_HOST"],
        user=os.environ["RDS_USER"],
        password=os.environ["RDS_PASSWORD"],
        database=os.environ["RDS_DATABASE"],
    )

    try:

        with connection:

            createdBy = ""
            subscriptionType = ""
            createdByCurrentUser = True

            getUserDetails = f"Select s.Subscription from users u, user_subscription s where u.Subscription = s.Id and u.Id = {data['userId']};"

            getCommentOfTalent = f"Select CommentId, c.UserId, Comment, ParentId, c.CreatedAt, c.UpdatedAt, UserName from talent t, comment_management c, users u where c.TalentId = {data['talentId']} and c.TalentId = t.TalentId and u.Id = c.UserId;"

            cur = connection.cursor(pymysql.cursors.DictCursor)

            cur.execute(getUserDetails)
            userData = cur.fetchall()

            userDetail = userData[0]

            cur.execute(getCommentOfTalent)
            allCommentsResult = cur.fetchall()

            for oneComment in allCommentsResult:
                if not oneComment["ParentId"] is None:
                    if oneComment["UserId"] == int(data["userId"]):
                        createdBy = "You"
                        createdByCurrentUser = True
                    else:
                        createdBy = oneComment["UserName"]
                        createdByCurrentUser = False

                    commentDict = {
                        "id": int(oneComment["CommentId"]),
                        "createdByCurrentUser": createdByCurrentUser,
                        "content": oneComment["Comment"],
                        "fullname": createdBy,
                        "parent": oneComment["ParentId"],
                        "created": str(oneComment["CreatedAt"]),
                        "modified": str(oneComment["UpdatedAt"]),
                    }

                    commentList.append(commentDict)

                else:
                    if oneComment["UserId"] == int(data["userId"]):
                        createdBy = "You"
                        createdByCurrentUser = True

                    else:
                        createdBy = oneComment["UserName"]
                        createdByCurrentUser = False

                    commentDict = {
                        "id": int(oneComment["CommentId"]),
                        "createdByCurrentUser": createdByCurrentUser,
                        "content": oneComment["Comment"],
                        "fullname": createdBy,
                        "parent": None,
                        "created": str(oneComment["CreatedAt"]),
                        "modified": str(oneComment["UpdatedAt"]),
                    }

                    commentList.append(commentDict)

            cur.close()
            response.body = {
                "commentResult": commentList,
                "Subscription": userDetail["Subscription"],
            }
            return response

    except Exception as e:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e


def create_comment(request, response):
    data = request.data
    now = datetime.now()
    count = 0
    paId = ""

    connection = pymysql.connect(
        host=os.environ["RDS_HOST"],
        user=os.environ["RDS_USER"],
        password=os.environ["RDS_PASSWORD"],
        database=os.environ["RDS_DATABASE"],
    )

    try:
        with connection:
            insert_comment_query = "Insert into comment_management (UserId, TalentId, Comment, ParentId, CreatedAt, UpdatedAt) Values (%s, %s, %s, %s, %s, %s);"
            userId = int(data["userId"])
            comment = data["content"]
            createdAt = now.strftime("%Y-%m-%d %H:%M:%S")
            updatedAt = now.strftime("%Y-%m-%d %H:%M:%S")
            parentId = 0
            if not data["parent"] is None:
                parentId = int(data["parent"])
            else:
                parentId = None
            talentId = int(data["talentId"])
            cur = connection.cursor()
            cur.execute(
                insert_comment_query,
                (userId, talentId, comment, parentId, createdAt, updatedAt),
            )
            connection.commit()
            cur.execute("Select LAST_INSERT_ID();")
            commentId = cur.fetchall()
            count = 1

            id = [id[0] for id in commentId]

            if count == 1:

                get_new_comment_query = f"Select CommentId, c.UserId, Comment, ParentId, c.CreatedAt, c.UpdatedAt, UrlLink, Name, Bio, FullName, us.Subscription from talent t, comment_management c, users u, user_subscription us where c.TalentId = {data['talentId']} and CommentId = {id[0]} and c.TalentId = t.TalentId and u.Id = c.UserId and u.Subscription = us.Id;"

                cur = connection.cursor(pymysql.cursors.DictCursor)
                cur.execute(get_new_comment_query)
                comment_result = cur.fetchall()

                oneResult = comment_result[0]
                if oneResult["ParentId"] is None:
                    paId = None
                else:
                    paId = int(oneResult["ParentId"])
                createdBy = ""
                createdByCurrentUser = True
                if int(oneResult["UserId"]) == int(data["userId"]):
                    createdBy = "You"
                    createdByCurrentUser = True
                else:
                    createdBy = oneResult["FullName"]
                    createdByCurrentUser = False

                commentDict = {
                    "id": int(oneResult["CommentId"]),
                    "parent": paId,
                    "content": oneResult["Comment"],
                    "fullname": createdBy,
                    "created": str(oneResult["CreatedAt"]),
                    "modified": str(oneResult["UpdatedAt"]),
                    "createdByCurrentUser": createdByCurrentUser,
                }
                response.body = commentDict

                cur.close()
                return response

    except Exception as e:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e
