import pymysql
import sys
import boto3
import json
from datetime import datetime

# from pymysql.constants import CLIENT


def get_comments(self, userId, talentId):

    commentList = []
    connection = pymysql.connect(
        host=self.host,
        user=self.user,
        password=self.password,
        database=self.database,
    )

    try:

        with connection:

            createdBy = ""
            createdByCurrentUser = True

            # getCommentOfTalent = f"Select CommentId, CustomerAccountId, Comment, ParentId, CreatedAt, UpdatedAt, UrlLink, Name, Bio, CustomerEmail from talent t, comment_management c, User u where c.TalentId = {talentId} and c.TalentId =  t.TalentId and u.UserId = c.CustomerAccountId;"

            getCommentOfTalent = f"Select CommentId, CustomerAccountId, Comment, ParentId, CreatedAt, UpdatedAt, UrlLink, Name, Bio from talent t, comment_management c where c.TalentId = {talentId} and c.TalentId =  t.TalentId;"

            cur = connection.cursor(pymysql.cursors.DictCursor)
            cur.execute(getCommentOfTalent)
            allCommentsResult = cur.fetchall()
            # print(allCommentsResult)

            for oneComment in allCommentsResult:
                if (oneComment["ParentId"] != None:
                    if oneComment["CustomerAccountId"] == userId:
                        createdBy = "You"
                        createdByCurrentUser = True
                    else:
                        createdBy = oneComment["CustomerEmail"]
                        createdByCurrentUser = False

                    commentDict = {
                        "id": oneComment["CommentId"],
                        "createdByCurrentUser": createdByCurrentUser,
                        "content": oneComment["Comment"],
                        "fullname": createdBy
                        "parent": int(oneComment["ParentId"]),
                        "created": datetime.strptime(
                            oneComment["CreatedAt"], "%d/%m/%Y %H:%M:%S"
                        ),
                        "modified": datetime.strptime(
                            oneComment["UpdatedAt"], "%d/%m/%Y %H:%M:%S"
                        ),
                        "UrlLink": oneComment["UrlLink"],
                        "Name": oneComment["Name"],
                        "Bio": oneComment["Bio"],
                    }
                    commentList.append(commentDict)
                else:
                    if oneComment["CustomerAccountId"] == userId:
                        createdBy = "You"
                        createdByCurrentUser = True
                    else:
                        createdBy = oneComment["CustomerEmail"]
                        createdByCurrentUser = False

                    commentDict = {
                        "id": oneComment["CommentId"],
                        "createdByCurrentUser": createdByCurrentUser,
                        "content": oneComment["Comment"],
                        "fullname": createdBy
                        "parent": None,
                        "created": datetime.strptime(
                            oneComment["CreatedAt"], "%d/%m/%Y %H:%M:%S"
                        ),
                        "modified": datetime.strptime(
                            oneComment["UpdatedAt"], "%d/%m/%Y %H:%M:%S"
                        ),
                        "UrlLink": oneComment["UrlLink"],
                        "Name": oneComment["Name"],
                        "Bio": oneComment["Bio"],
                    }
                    commentList.append(commentDict)

            return commentList

    finally:
        # connection.close()
        return


def main():
    retrieveComment = CommentManagement()
    cmtList = retrieveComment.getComments(1, 4)
    print(cmtList)


if __name__ == "__main__":
    main()
