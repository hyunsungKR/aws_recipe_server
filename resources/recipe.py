from flask import request
from flask_restful import Resource

from mysql_connection import get_connection
from mysql.connector import Error
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

# API 를 만들기 위한 클래스 작성.
# class(클래스) 란?? - 변수와 함수로 구성된 묶음이다.
# 클래스는 상속이 가능하다!
# API를 만들기 위해서는, flask_restful 라이브러리의
# Resource 클래스를 상속해서 만들어야 한다.

class RecipeListResource(Resource) : 
    

    # API를 처리하는 함수 개발
    # HTTP Method를 보고! 똑같이 만들어준다.

    # jwt 토큰이 필수라는 뜻! : 토큰이 없으면 이 API는 실행이 안 된다.
    @jwt_required()
    def post(self) :




        # 1. 클라이언트가 보내준 데이터가 있으면
        #    그 데이터를 받아준다.
        data = request.get_json()

        # 1-1 헤더에JWT 토큰이 있으면 토큰 정보를 받아준다
        user_id = get_jwt_identity()



        # 2. 이 레시피정보를 DB에 저장해야한다.
        
        try :
            ### 1. DB에 연결
            connection = get_connection()

            ### 2. 쿼리문 만들기
            query = '''insert into recipe
                    (name,description,num_of_servings,cook_time,directions,user_id)
                    values
                    (%s,%s,%s,%s,%s,%s);'''
            ### 3. 쿼리에 매칭되는 변수 처리 해준다. 튜플로!
            record = ( data['name'],data['description'],data['num_of_servings'],data['cook_time'],data['directions'],user_id )

            ### 4. 커서를 가져온다.
            cursor=connection.cursor()

            ### 5. 쿼리문을 커서로 실행한다.
            cursor.execute(query, record)

            ### 6. 커밋을 해줘야 DB에 완전히 반영된다.
            connection.commit()

            ### 7. 자원 해제
            cursor.close()
            connection.close()

        except Error as e :

            print(e)
            cursor.close()
            connection.close()

            return{"result" : "fail", "error" : str(e)} , 500



        # API를 끝낼때는
        # 클라이언트에 보내줄 정보(json)와 http 상태 코드를
        # 리턴한다.
        return {"result" : "success"} , 200

    def get(self) :
        # 1. 클라이언트로부터 데이터를 받아온다.
        # 없다.

        # 2. db에 저장된 데이터를 가져온다.
        try :
            connection = get_connection()

            query = '''select * from recipe;'''

            ## 중요!!!! select 문은 
            ## 커서를 가져올 때 dictionary = True로 해준다
            cursor = connection.cursor(dictionary=True)

            cursor.execute(query)

            result_list=cursor.fetchall()

            print(result_list)
            
            # 중요 ! db에서 가져온 timestamp는
            # 파이썬에서 datetime으로 자동 변환된다.
            # 그런데 문제는 !!! 우리는 json으로
            # 클라이언트한테 데이터를 보내줘야 하는데
            # datetime은 json으로 보낼 수 없다.
            # 따라서 시간을 문자열로 변환해서 보내준다.
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
            return{"result":"fail","error":str(e)}, 500
        
        return {"result" : 'seccess','items':result_list,'count':len(result_list)}, 200


class RecipeResource(Resource) :

    def get(self, recipe_id) : 

        # 1. 클라이언트로부터 정보를 가져온다.
        # print(recipe_id)
        
        # 2. 디비로부터 해당 레시피아이디에 맞는 레시피데이터를 가져온다.

        try : 
            connection = get_connection()
            query = '''select * 
                    from recipe
                    where id = %s ;'''
            
            record = (recipe_id, )
            
            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['created_at'] = row['created_at'].isoformat()
                result_list[i]['updated_at'] = row['updated_at'].isoformat()
                i = i + 1
            
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'result' : 'fail', 'error' : str(e)}, 500
        
        if len(result_list) == 0 :
            return {'result' : 'fail', 'message' : '데이터가 없습니다.'}, 400

        return{'result' : 'success' , 'item' : result_list[0]}, 200

    @jwt_required()
    def put(self, recipe_id) : 

        data = request.get_json()

        user_id = get_jwt_identity()

        try : 
            connection = get_connection()
            query = '''update recipe
                    set
                    name = %s,
                    description = %s,
                    num_of_servings = %s,
                    cook_time = %s,
                    directions = %s
                    where id = %s and user_id = %s;'''
            
            record = (data['name'],data['description'],data['num_of_servings'],data['cook_time'],data['directions'],recipe_id,user_id)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500

        return {'result' : 'success' }, 200

    @jwt_required()
    def delete(self,recipe_id) :

        user_id=get_jwt_identity()

        try :
            connection = get_connection()
            query = '''delete from recipe
                    where id = %s and user_id = %s;'''
            record = (recipe_id,user_id)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()
            connection.close()
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'result':'fail','error':str(e)}, 500

        return {'result':'success'},200        

class RecipePublishResource(Resource):
    @jwt_required()
    def put(self,recipe_id) :
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''update recipe
                    set is_publish = 1
                    where id = %s and user_id = %s;'''
            record = (recipe_id,user_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500

        return {'result' : 'success' }, 200
    @jwt_required()
    def delete(self,recipe_id) :
        user_id = get_jwt_identity()
        try :
            connection = get_connection()
            query = '''update recipe
                    set is_publish = 0
                    where id = %s and user_id = %s;'''
            record = (recipe_id,user_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500

        return {'result' : 'success' }, 200

class MyRecipeListResource(Resource):
    @jwt_required()
    def get(self) :
        
        user_id=get_jwt_identity()
        try :
            connection = get_connection()

            ### 내가 작성한 레시피인지 확인 ###
            ### recipe_id로 레시피를 가져온다.
            ### db에 저장되어있는 user_id 컬럼의 값이
            ### 토큰에서 봅은 user_id랑 같은지 확인
            

            query = '''select *
                    from recipe
                    where user_id=%s;'''
            record = (user_id,)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)

            result_list=cursor.fetchall()

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
            return {'error' : str(e)}, 500



        return {'result':'success','items':result_list,'count':len(result_list)},200