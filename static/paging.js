function paging(totalData, dataPerPage, pageCount, currentPage) {

    totalPage = Math.ceil(totalData / dataPerPage); //총 페이지 수

    if (totalPage < pageCount) {
        pageCount = totalPage;
    }

    let pageGroup = Math.ceil(currentPage / pageCount); // 페이지 그룹
    let last = pageGroup * pageCount; //화면에 보여질 마지막 페이지 번호

    let first = last - (pageCount - 1); //화면에 보여질 첫번째 페이지 번호
    let next = last + 1;
    let prev = first - 1;

    if (last > totalPage) {
        last = totalPage;
    }

    let pageHtml = ``;

    if (prev > 0) {
        pageHtml += `<li><a href='#' id='prev'> 이전 </a></li>`;
    }

    //페이징 번호 표시
    for (var i = first; i <= last; i++) {
        if (currentPage == i) {
            pageHtml += `<li class='on'><a href='#' id="${i}">${i}</a></li>`;
        } else {
            pageHtml += `<li><a href='#' id='"${i}"'>${i}</a></li>`;
        }
    }

    if (last < totalPage) {
        pageHtml += `<li><a href='#' id='next'> 다음 </a></li>`;
    }

    $("#pagingul").html(pageHtml);

    //페이징 번호 클릭 이벤트
    $("#pagingul li a").click(function () {
        let $id = $(this).attr("id");
        selectedPage = $(this).text();

        if ($id == "next")
            selectedPage = next;
        if ($id == "prev")
            selectedPage = prev;

        //페이징 표시 재호출
        paging(totalData, dataPerPage, pageCount, selectedPage);
        //글 목록 표시 재호출
        displayData(selectedPage, dataPerPage, comments);
    });
}

//현재 페이지(currentPage)와 페이지당 글 개수(dataPerPage) 반영
function displayData(currentPage, dataPerPage, comments) {

    let chartHtml = ``;

    //Number로 변환하지 않으면 아래에서 +를 할 경우 스트링 결합이 되어버림..
    currentPage = Number(currentPage);
    dataPerPage = Number(dataPerPage);

    // currentpage=3일시 (20;30; 1++) why? 데이터는 0부터 시작하므로 0~9 index= 1page, 10~19
    // index= 2page, 20~29 index = 3page
    for (
        var i = (currentPage - 1) * dataPerPage;
        i < (currentPage - 1) * dataPerPage + dataPerPage;
        i++
    ) {
        if (i >= comments.length) {
            break
        }

        chartHtml +=
            `<div class="card-header">
             <span class="blockquote mb-0">
            <p>${comments[i]['comment']}</p>
            </span>
        </div>`;
    }
    $("#card-box").html(chartHtml);
}