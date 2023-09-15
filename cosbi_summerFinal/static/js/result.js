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


function getInterval_FromDataTable(Data){
    var intervalResult = []
    var colorType = "orange"
    for (unit of Data){
        var start_point = unit.start_point;
        var end_point = unit.end_point;
        var name = unit.name;
        if (name.includes("UTR")){
            var unit_interval = {
                "start":start_point-1,
                "end":end_point,
                "class":"UTR",
            };
            intervalResult.push(unit_interval);
        } 
        
        
        if(name.includes("Exon")){
            var unit_interval = {
                "start":start_point-1,
                "end":end_point,
                "class":colorType,
            };

            intervalResult.push(unit_interval);

            if (colorType === "orange"){                
                colorType = "yellow";
            }
            else{colorType = "orange";}
        }
    }
    return intervalResult;
    }

   

function getColorClass(intervalTableType,index){
    if (intervalTableType === "unspliced"){var intervalTable = unsplicedIntervalTable;}
    else if (intervalTableType === "spliced"){var intervalTable = splicedIntervalTable;}
    else{return "";}

    returnClass = ""
    for (const coordinate of intervalTable){
        if (index >= coordinate.start && index < coordinate.end){
            returnClass += coordinate.class;
            returnClass += " ";
        }
    }
    return returnClass;
}

function insertSequence(sequence, containerID){
    function formatSequence(sequence){
        const GROUP_SIZE = 10;
        const LINE_SIZE = 50;
        let formattedSequence = "";
        if (containerID === "unsplice_sequence_container"){var intervalTableType = "unspliced";}
        else if (containerID === "splice_sequence_container"){var intervalTableType = "spliced";}
        else{var intervalTableType = "NONE";}

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
            

            var colorClass = getColorClass(intervalTableType, i);
            formattedSequence += `<span class="base ${colorClass}">${sequence[i]}</span>`;    
        }
        return formattedSequence;
    }

    const sequenceContainer = document.getElementById(containerID);
    sequenceContainer.innerHTML = '<p class="text-same-case">'+formatSequence(sequence)+'<p/>'
}


function drawScaleLinear(containerID, seqLength){
    var parentDiv = d3.select("#"+containerID); 
    var width = 1600;
    var height = 200;
    var svg = d3.select("#"+containerID)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    if (containerID === "unspliced_scaleLinear_container"){var intervalTable = unsplicedIntervalTable;}
    else if (containerID === "spliced_scaleLinear_container"){var intervalTable = splicedIntervalTable;}
    else{return;}

    var xScale = d3.scaleLinear()
        .domain([0, seqLength])
        .range([30, width - 30]);

    var tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    svg.append("g")
        .attr("transform", "translate(0, 110)")
        .call(d3.axisBottom(xScale));

    svg.selectAll("rect")
        .data(intervalTable)
        .enter()
        .append("rect")
        .attr("x", function (d) { return xScale(d.start); })
        .attr("y", function(d){
            if (d.class ==="UTR"){return (height / 2 - 30);}
            else{return (height / 2 - 20);}} )
        
        .attr("width", function (d) { 
            return xScale(d.end) - xScale(d.start); })
        .attr("height", function(d){
                        if (d.class ==="UTR"){return 20;}
                        else{return 30;}
        })
        .style("fill", function (d) { 
                if (d.class ==="UTR"){return "grey";}
                else{return d.class;}
             })
             .on("mouseover", function (d) {
                var intervalData = d3.select(this).data()[0]; // 获取绑定到当前元素上的数据
                var rect = this.getBoundingClientRect(); // 获取元素相对于视口的位置信息
                var pageX = rect.left + window.scrollX; // 计算鼠标相对于文档的X坐标
                var pageY = rect.top + window.scrollY; // 计算鼠标相对于文档的Y坐标
            
                tooltip.transition()
                    .duration(200)
                    .style("opacity", 0.9);
                tooltip.html("Start: " + (parseInt(intervalData.start, 10)+1) + "<br/>End: " + intervalData.end)
                    .style("left", (pageX) + "px")
                    .style("top", (pageY - 28) + "px");
            })
            .on("mouseout", function (d) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            });
            
    
        
    d3.selectAll("text").style("font-size", "16px");

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
            proteinSeq = Data["proteinSeq"];
            if(proteinSeq === ""){
                var container = document.getElementById("protein_button");
                container.style.display = "none";
            }
            else{
                var container = document.getElementById("protein_button");
                container.style.display = "block";
            }   
            unsplicedIntervalTable = getInterval_FromDataTable(Data["unsplicedData"])
            splicedIntervalTable = getInterval_FromDataTable(Data["splicedData"])
            
            insertSequence(unsplicedSeq, "unsplice_sequence_container");
            insertSequence(splicedSeq, "splice_sequence_container");
            
            insertSequence(proteinSeq, "protein_sequence_container");
            console.log(unsplicedIntervalTable);

            drawScaleLinear("unspliced_scaleLinear_container",unsplicedSeq.length);
            drawScaleLinear("spliced_scaleLinear_container",splicedSeq.length);

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


