import pymysql
import os
from datetime import datetime
from lib.webexception import WebException
from http import HTTPStatus


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
            createdByCurrentUser = True

            getCommentOfTalent = f"Select CommentId, c.UserId, Comment, ParentId, c.CreatedAt, c.UpdatedAt, UrlLink, Name, Bio, FullName from talent t, comment_management c, user u where c.TalentId = {data['talentId']} and c.TalentId = t.TalentId and u.Id = c.UserId;"

            cur = connection.cursor(pymysql.cursors.DictCursor)
            cur.execute(getCommentOfTalent)
            allCommentsResult = cur.fetchall()

            for oneComment in allCommentsResult:
                if not oneComment["ParentId"] is None:
                    if oneComment["UserId"] == int(data["userId"]):
                        createdBy = "You"
                        createdByCurrentUser = True
                    else:
                        createdBy = oneComment["FullName"]
                        createdByCurrentUser = False

                    commentDict = {
                        "id": int(oneComment["CommentId"]),
                        "createdByCurrentUser": createdByCurrentUser,
                        "content": oneComment["Comment"],
                        "fullname": createdBy,
                        "parent": int(oneComment["ParentId"]),
                        "created": oneComment["CreatedAt"],
                        "modified": oneComment["UpdatedAt"],
                        "UrlLink": oneComment["UrlLink"],
                        "Name": oneComment["Name"],
                        "Bio": oneComment["Bio"],
                    }
                    commentList.append(commentDict)
                else:
                    if oneComment["UserId"] == int(data["userId"]):
                        createdBy = "You"
                        createdByCurrentUser = True
                    else:
                        createdBy = oneComment["FullName"]
                        createdByCurrentUser = False

                    commentDict = {
                        "id": int(oneComment["CommentId"]),
                        "createdByCurrentUser": createdByCurrentUser,
                        "content": oneComment["Comment"],
                        "fullname": createdBy,
                        "parent": None,
                        "created": oneComment["CreatedAt"],
                        "modified": oneComment["UpdatedAt"],
                        "UrlLink": oneComment["UrlLink"],
                        "Name": oneComment["Name"],
                        "Bio": oneComment["Bio"],
                    }
                    commentList.append(commentDict)
                    response.body = commentList
                    cur.close()
            return response

    except Exception as e:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e


def create_comment(request, response):
    data = request.data
    now = datetime.now()
    count = 0

    connection = pymysql.connect(
        host=os.environ["HOST"],
        user=os.environ["USER"],
        password=os.environ["PASSWORD"],
        database=os.environ["DATABASE"],
    )

    try:
        with connection:
            insert_comment_query = "Insert into comment_management (UserId, TalentId, Comment, ParentId, CreatedAt, UpdatedAt) Values (%s, %s, %s, %s, %s, %s);"
            userId = int(data["userId"])
            comment = data["content"]
            createdAt = now.strftime("%d/%m/%Y %H:%M:%S")
            updatedAt = now.strftime("%d/%m/%Y %H:%M:%S")
            parentId = 0
            if str(data["parent"]) != "":
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
                get_new_comment_query = f"Select CommentId, c.UserId, Comment, ParentId, c.CreatedAt, c.UpdatedAt, UrlLink, Name, Bio, FullName from talent t, comment_management c, user u where c.TalentId = t.TalentId and u.Id = c.UserId and CommentId = {id[0]} and c.TalentId = {data['talentId']};"

                cur = connection.cursor(pymysql.cursors.DictCursor)
                cur.execute(get_new_comment_query)
                comment_result = cur.fetchall()
                oneResult = comment_result[0]

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
                    "parent": int(oneResult["ParentId"]),
                    "content": oneResult["Comment"],
                    "fullname": createdBy,
                    "created": oneResult["CreatedAt"],
                    "modified": oneResult["UpdatedAt"],
                    "createdByCurrentUser": createdByCurrentUser,
                }
                response.body = commentDict
                cur.close()
            return response

    except Exception as e:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e

