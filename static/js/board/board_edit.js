$(document).ready(function() {
        $('#summernote').summernote({
            placeholder: '내용을 입력해주세요.',
            tabsize: 2,
            height: 450,
            lang: 'ko-KR',
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'clear']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'picture', 'video']],
                ['view', ['fullscreen', 'codeview']]
            ]
        });
    });

    function confirmEdit() {
        // 알림창을 띄우고 사용자가 '확인'을 누르면 true를 반환해서 폼이 전송됨
        alert("수정이 완료되었습니다!");
        return true;
    }