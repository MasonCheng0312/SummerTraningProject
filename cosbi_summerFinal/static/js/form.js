$(document).ready(function(){

    $('#submit').click(function(){
        
        $.ajax({
            headers: { 'X-CSRFToken': csrf_token },
            type: 'POST',
            url: '/web_tool/ajax_data/', 
            data: $('#ajax_form').serialize(),
            success: function(response){ 
                var data = response;
                var tableHTML = '<table class="table table-bordered">';
                tableHTML += '<thead><tr><th>GeneID</th><th>TranscriptID</th><th># of transcript</th></tr></thead>';
                tableHTML += '<tbody>';

                for (var i = 0; i < data.length; i++) {
                    var row = data[i];
                    tableHTML += '<tr><td>' + row.gene_id + '</td><td>' + row.transcript_id + '</td><td>' + row.field_oftranscripts + '</td></tr>';
                }

                tableHTML += '</tbody></table>';
                $("#table-container").html(tableHTML);
                applyTableStyles();
            },
            error: function(){
                alert('Something error');
            },
        });
    });
});

function applyTableStyles() {
    $(".table-container").css({
        margin: "0 auto",
        "max-width": "calc(100% - 40px)",
        padding: "20px",
        "box-sizing": "border-box"
    });

    // 可以添加其他你需要的樣式
}