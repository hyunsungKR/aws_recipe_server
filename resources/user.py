from flask import request
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
from email_validator import validate_email,EmailNotValidError
from flask_jwt_extended import create_access_token,jwt_required,get_jwt





from utils import check_password, hash_password

class UserRegisterResource(Resource) :
    def post(self) :
    
        #{"username":"홍길동",
        #"email":"abc@naver.com",
        #"password":"1234"}

        #1. 클라이언트가 보낸 데이터를 받아준다.
        data = request.get_json()

        #2. 이메일 주소형식이 올바른지 확인한다.
        try :
            validate_email(data["email"])
        except EmailNotValidError as e :
            print(str(e))
            return{'error':str(e)},400
        #3. 비밀번호의 길이가 유효한지 체크한다.
        # 만약 비밀번호가 4자리 이상 12자리 이하면

        if len(data['password']) < 4 or len(data['password']) > 12 :
            return {'error':'비밀번호 길이 확인'},400

        #4. 비밀번호를 암호화한다.
        hashed_password=hash_password(data['password'])
        print(hashed_password)
        #5. db에 회원 정보를 저장한다.
        try : 
            connection = get_connection()
            query = '''insert into user
                    (username,email,password)
                    values
                    (%s,%s,%s);'''
            record = (data['username'],data['email'],hashed_password)

            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            ### DB에 회원가입하여, insert된 후에
            ### user 테이블의 id값을 가져오는 코드!
            user_id=cursor.lastrowid

            cursor.close()
            connection.close()
        
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error':str(e)},500

        ## user_id를 바로 클라이언트에게 보내면 안되고,
        ## JWT로 암호화해서 인증토큰을 보낸다.

        access_token=create_access_token(user_id)



        return {'result':'success','access_token':access_token}


class UserLoginResource(Resource) :
    def post(self) :
        #{"email":"a01090693658@gmail.com",
        #"password":"12341231"}
        data=request.get_json()

        #2. DB로 부터 해당 유저의 데이터를 가져온다.
        try :
            connection = get_connection()
            query = '''select *
                    from user
                    where email = %s;'''
            record = (data['email'],)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)

            result_list=cursor.fetchall()

            if len(result_list) == 0 :
                return {'error':'회원가입한 사람 아닙니다.'},400

            i = 0
            for row in result_list :
                result_list[i]['created_at']=row['created_at'].isoformat()
                result_list[i]['updated_at']=row['updated_at'].isoformat()
                i = i+1
            
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'error':str(e)}, 500

        print(result_list)

        # 3. 비밀번호가 맞는지 확인한다.
        check = check_password(data['password'],result_list[0]['password'])

        if check == False :
            return {'error':'비밀번호가 틀립니다.'},400
        
        # 4. JWT토큰을 만들어서 클라이언트에게 보낸다.
        access_token = create_access_token(result_list[0]['id'])
    
        return{'result':'success','access_token':access_token}, 200

### 로그아웃 ###
# 로그아웃된 토큰을 저장할 set 만든다.

jwt_blacklist = set()

class UserLogoutResource(Resource):
    @jwt_required()
    def post(self) :
        
        jti=get_jwt()['jti']
        print(jti)
        jwt_blacklist.add(jti)

        return {'result':'success'},200
