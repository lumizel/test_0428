/* ===== 게시글 숨김 ===== */
async function hideBoard(memberId, boardId) {
    if (!confirm('이 게시글을 숨기겠습니까?')) return;
    const res = await fetch(`/admin/members/${memberId}/board/${boardId}/delete`, {
        method: 'POST'
    });
    if (res.ok) { showToast('✅ 처리되었습니다.'); location.reload(); }
    else showToast('❌ 처리 실패', 'error');
}

/* ===== 댓글 삭제 ===== */
async function deleteComment(memberId, commentId) {
    if (!confirm('이 댓글을 삭제하겠습니까?')) return;
    const res = await fetch(`/admin/members/${memberId}/comment/${commentId}/delete`, {
        method: 'POST'
    });
    if (res.ok) { showToast('✅ 삭제되었습니다.'); location.reload(); }
    else showToast('❌ 삭제 실패', 'error');
}

/* ===== 휴지통 영구삭제 ===== */
async function deleteTrash(memberId, boardId) {
    if (!confirm('영구 삭제하면 복구할 수 없습니다. 진행하겠습니까?')) return;
    const res = await fetch(`/admin/members/${memberId}/trash/${boardId}/delete`, {
        method: 'POST'
    });
    if (res.ok) { showToast('✅ 영구 삭제되었습니다.'); location.reload(); }
    else showToast('❌ 삭제 실패', 'error');
}