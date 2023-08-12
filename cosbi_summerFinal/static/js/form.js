$(document).ready(function(){
    $('#submit').click(function(){
        $.ajax({
            headers: { 'X-CSRFToken': csrf_token },
            type: 'POST',
            url: '/web_tool/ajax_data/', 
            data: $('#ajax_form').serialize(),
            success: function(response){ 
                var data = response;
                
                // 移除先前的資料表，以避免重複初始化
                if ($.fn.DataTable.isDataTable('#result_table')) {
                    $('#result_table').DataTable().destroy();
                    $('#result_table').empty();
                }

                // 初始化新的 DataTables 資料表
                $("#result_table").DataTable({
                    "data": data,
                    "searching": false,
                    "columns": [
                        {data: "gene_id", title: "Gene_Name"},
                        {data: "transcript_id", title: "Transcript_ID"},
                        {data: "field_oftranscripts", title: "Number of transcript"}
                    ]
                });
            },
            error: function(){
                alert('Something error');
            },
        });
    });
});
