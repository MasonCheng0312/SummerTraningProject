$(document).ready(function () {
    $('#submit').click(function () {
        $.ajax({
            headers: { 'X-CSRFToken': csrf_token },
            type: 'POST',
            url: '/web_tool/ajax_data/',
            data: $('#ajax_form').serialize(),
            success: function (response) {
                if (response["error"] != "No Error") {
                    alert(response["error"])
                }

                else {
                    var target = $(input_data).val();                     
                    var data = [response["response"]];
                    // DataTable需要的資料格式是List[Dict]
                    // 媽的= =

                    // 移除先前的資料表，以避免重複初始化
                    if ($.fn.DataTable.isDataTable('#result_table')) {
                        $('#result_table').DataTable().destroy();
                        $('#result_table').empty();
                    }

                    // 初始化新的 DataTables 資料表
                    $("#result_table").DataTable({
                        "data": data,
                        "searching": false,
                        "paging": false,
                        "info": false,
                        "columns": [
                            { data: "gene_id", title: "WBgene Name" },
                            { data: "transcript_id", title: "Transcript ID" },
                            { data: "gene_name", title: "Gene Name" },
                            { data: "other_name", title: "Other Name" },
                            { data: "field_oftranscripts", title: "Number of transcript" }
                        ],
                        "createdRow": function(row, data, dataIndex){
                            if (data.gene_id === target){
                                $(row).attr("style", "background-color:lightblue")
                            }
                            if (data.transcript_id === target){
                                $(row).attr("style", "background-color:lightblue")
                            }
                            if (data.gene_name === target) {
                                $(row).attr("style", "background-color:lightblue")
                            }
                            if (data.other_name === target){
                                $(row).attr("style", "background-color:lightblue")
                            }
                        },                        
                    });

                    if ($.fn.DataTable.isDataTable('#link_table')) {
                        $('#link_table').DataTable().destroy();
                        $('#link_table').empty();
                    }

                    var transList = response["transID"];
                    $("#link_table").DataTable({
                        "data": transList,
                        "searching": false,
                        "paging": false,
                        "info": false,
                        "columns": [
                            {
                                data: "transcriptID",
                                title: "Transcript ID",
                                render: function (data, type, row) {
                                    var url = "../detail_data/?name=" + encodeURIComponent(data);
                                    return '<a href="' + url + '" target="_blank">' + data + '</a>';
                                }
                            },
                        ],
                        "createdRow": function(row, data, dataIndex){
                            if (data.transcriptID === target){
                                $(row).find("td").attr("style", "background-color:lightblue")
                            }
                        }
                    });
                }

            },

            error: function () {
                alert('Something error');
            },
        });
    });
});
