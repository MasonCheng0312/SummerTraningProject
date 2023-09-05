function callViewsForTransData() {
    var currentUrl = window.location.href;
    var targetUrl = currentUrl.replace("/detail_data/", "/getData/")
    return fetch(targetUrl)
};


function loadDatatable(Data) {//Data為一json檔
    var unsplicedData = Data["unsplicedData"]
    var splicedData = Data["splicedData"]
    if ($.fn.DataTable.isDataTable('#unsplice_data_table')) {
        $('#unsplice_data_table').DataTable().destroy();
        $('#unsplice_data_table').empty();
    }

    if ($.fn.DataTable.isDataTable('#splice_data_table')) {
        $('#splice_data_table').DataTable().destroy();
        $('#splice_data_table').empty();
    }

    $("#unsplice_data_table").DataTable({
        "data": unsplicedData,
        "searching": false,
        "paging": false,
        "info": false,
        "autoWidth": false,
        "order": [[1, 'asc']],
        "columns": [
            { data: "name", title: "Name", width: "33%" }, // 设置宽度为 33%
            { data: "start_point", title: "Start Location", width: "33%" }, // 设置宽度为 33%
            { data: "end_point", title: "End Location", width: "34%" }, // 设置宽度为 34%
        ],

    })

    $("#splice_data_table").DataTable({
        "data": splicedData,
        "searching": false,
        "paging": false,
        "info": false,
        "autoWidth": false,
        "order": [[1, 'asc']],
        "columns": [
            { data: "name", title: "Name", width: "33%" }, // 设置宽度为 33%
            { data: "start_point", title: "Start Location", width: "33%" }, // 设置宽度为 33%
            { data: "end_point", title: "End Location", width: "34%" }, // 设置宽度为 34%
        ],

    })

}


function insertSequence(sequence, containerID){
    function formatSequence(sequence){
        const GROUP_SIZE = 10;
        const LINE_SIZE = 50;
        let formattedSequence = "";
        var space = ""
        
        for (let i = 0; i < sequence.length; i++){
            if (i % LINE_SIZE === 0) {
                if (i !== 0) {
                    formattedSequence += "<br>";
                }                
                formattedSequence += `<span class="line-number">${i + 1}</span> `;
            }
    
            if (i % GROUP_SIZE === 0 && i !== 0) {
                formattedSequence += " ";
            }
            
            formattedSequence += `<span class="base">${sequence[i]}</span>`;    
        }
        return formattedSequence;
    }

    const sequenceContainer = document.getElementById(containerID);
    sequenceContainer.innerHTML = '<p class="text-same-case">'+formatSequence(sequence)+'<p/>'
}




function toggleContainerVisibility(containerID) {
    var container = document.getElementById(containerID);
    if (container.style.display === "none") {
        container.style.display = "block";
    }
    else {
        container.style.display = "none";
    }
}


window.onload = function () {
    callViewsForTransData()
        .then(Response => {
            if (!Response.ok) {
                throw new Error("Response was not ok!");
            }
            return Response.json();
        })
        .then(Data => {
            loadDatatable(Data);
            unsplicedSeq = Data["unsplicedSeq"];
            splicedSeq = Data["splicedSeq"];
            insertSequence(unsplicedSeq, "unsplice_sequence_container");
            insertSequence(splicedSeq, "splice_sequence_container");
        })
        .catch(error => {
            console.error("There was some error in fetch operation :", error);
            throw error;
        });

    document.getElementById("unspliced_button").addEventListener("click", function () {
        toggleContainerVisibility("unspliced_content");
    });

    document.getElementById("spliced_button").addEventListener("click", function () {
        toggleContainerVisibility("spliced_content");
    });

    document.getElementById("protein_button").addEventListener("click", function () {
        toggleContainerVisibility("protein_content");
    });


};


