import os
import uuid

from LMS.common import Session, fetch_query, execute_query, upload_file, get_file_info


class PostService :
    # 파일 게시물 - 저장
    @staticmethod
    def save_post(member_id, title, content, files=None):
        """ 게시물 저장 및 파일 Cloudinary 업로드 (트랜잭션 처리) """
        post_id = execute_query("INSERT INTO posts (member_id, title, content) VALUES (%s, %s, %s)", (member_id, title, content))
        if files:
            for file in files:
                if file and file.filename != '':
                    file_url = upload_file(file, folder="posts")
                    if file_url:
                        origin_name = file.filename
                        save_name = file_url
                        file_path = file_url
                        sql_file = """
                            INSERT INTO attachments (post_id, origin_name, save_name, file_path)
                            VALUES (%s, %s, %s, %s)
                        """
                        return execute_query(sql_file, (post_id, origin_name, save_name, file_path))

    # 파일 게시물 - 목록
    @staticmethod
    def get_posts() :
        """작성자 이름과 첨부파일 개수를 함께 조회"""
        sql = """
            SELECT p.*, m.name as writer_name,
                   (SELECT COUNT(*) FROM attachments WHERE post_id = p.id) as file_count
            FROM posts p
            JOIN members m ON p.member_id = m.id
            ORDER BY p.created_at DESC
        """
        return fetch_query(sql)

    # 파일 게시물 - 자세히 보기
    @staticmethod
    def get_post_detail(post_id):
        # 1. 조회수 +1 (기존 유지)
        execute_query("UPDATE posts SET view_count = view_count + 1 WHERE id = %s", (post_id,))

        # 2. 게시글 본문 조회 (기존 유지)
        sql_post = """
                SELECT p.*, m.name as writer_name 
                FROM posts p
                JOIN members m ON p.member_id = m.id
                WHERE p.id = %s
            """
        post = fetch_query(sql_post, (post_id,), one=True)

        if not post:
            return None, None

        # 3. 파일 목록 조회
        # (DB에는 Cloudinary URL이 'save_name'이나 'file_path'에 저장되어 있습니다)
        sql_files = "SELECT * FROM attachments WHERE post_id = %s"
        raw_files = fetch_query(sql_files, (post_id,))

        # 4. 파일 정보 가공 (uploader.py의 메서드 사용)
        files = []
        for file in raw_files:
            # DB에 저장된 URL (저장 방식에 따라 save_name 혹은 file_path 사용)
            # 앞서 save_post에서 save_name = file_url 로 저장했으므로 save_name을 씁니다.
            file_url = file.get('save_name') or file.get('file_path')

            # Cloudinary 정보 생성
            file_info = get_file_info(file_url)

            # 기존 DB 정보에 Cloudinary 가공 정보를 합칩니다.
            # (프론트엔드에서 file.original_url, file.thumbnail_url 등으로 접근 가능)
            if file_info:
                file.update(file_info)

            files.append(file)

        return post, files

    # 파일 게시물 - 삭제
    @staticmethod
    def delete_post(post_id, upload_folder='uploads/'):
        """게시글 및 관련 실제 파일 삭제"""
        # files = fetch_query("SELECT save_name FROM attachments WHERE post_id = %s", (post_id,))
        # if files:
        #     for f in files:
        #         file_path = os.path.join(upload_folder, f['save_name'])
        #
        #         if os.path.exists(file_path):
        #             os.remove(file_path)  # 실제 하드에서 삭제를 진행한다.
        return execute_query("DELETE FROM posts WHERE id = %s", (post_id,))

    # 파일 게시물 - 수정
    @staticmethod
    def update_post(post_id, title, content, files=None):
        """ 게시글 수정 및 다중 파일 교체 (execute_query 적용) """
        try:
            # 1. 게시글 기본 정보(제목, 내용) 수정
            # execute_query가 내부적으로 commit/rollback을 다 처리해줍니다.
            sql_update = "UPDATE posts SET title=%s, content=%s WHERE id=%s"
            execute_query(sql_update, (title, content, post_id))

            # 2. 새 파일들이 들어왔을 경우에만 기존 파일 교체
            # (files 리스트가 있고, 그 안에 빈 파일('')이 아닌 실제 파일이 하나라도 있는지 확인)
            if files and any(f.filename != '' for f in files):

                # A. 기존 첨부파일 DB 기록 삭제 (Link 끊기)
                # Cloudinary 파일은 굳이 삭제하지 않아도 되므로 DB만 정리합니다.
                execute_query("DELETE FROM attachments WHERE post_id = %s", (post_id,))

                # B. 새로운 파일들 Cloudinary 업로드 및 DB 저장
                for file in files:
                    if file and file.filename != '':

                        # Cloudinary 업로드
                        file_url = upload_file(file, folder="posts")

                        if file_url:
                            # DB 저장 (execute_query 사용)
                            sql_insert = """
                                    INSERT INTO attachments (post_id, origin_name, save_name, file_path)
                                    VALUES (%s, %s, %s, %s)
                                """
                            # Cloudinary URL을 save_name과 file_path 모두에 저장
                            execute_query(sql_insert, (post_id, file.filename, file_url, file_url))

            return True

        except Exception as e:
            print(f"❌ Error updating post: {e}")
            return False

