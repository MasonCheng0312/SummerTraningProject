function callPython() {
    var currentUrl = window.location.href;
    var targetUrl = currentUrl.replace("/piRNA_taget_predict/", "/getPredictResult/");
    return fetch(targetUrl)
};

function loadDatatable(Data, TableID) {
    function initialDatatable(selectName){
        
        if ($.fn.DataTable.isDataTable(selectName)) {
            $(selectName).DataTable().destroy();
            $(selectName).empty();
        }
    }

    var selectName = '#' + TableID

    initialDatatable(selectName);

    $(selectName).DataTable({
        "data": Data,
        "searching": false,
        "paging": false,
        "info": false,
        "autowidth":false,
        "columns": [
            { data: "name", title: "piRNA"},
            { data: "score", title:"piRNA targeting score"},
            { data: "location", title: "targeted region on input sequence"},
            { data: "#mismatch", title: "# of mismatch"},
            { data: "mismatchPostion with Tag", title: "mismatch position on piRNA"},
            { data: "#Non_GU pair seed region", title: "# of non-GU-pair in seed region"},
            { data: "#GU pair seed region", title: "# of GU-pair in seed region"},
            { data: "#Non_GU pair Non_seed region", title: "# of non-GU-pair in non-seed region"},
            { data: "#GU pair Non_seed region", title: "# of GU-pair in non-seed region"},
            { data: "seq tag in target region", title: "pairing", className:'pairing-sequence', width:"400"},
        ],

    })
};

function drawScaleLinear(seqLength, seqTable, piRNA_Location){
    var width = 1600;
    var height = 200;

    var tooltip2 = d3.select("#pirScan")
        .append("div")
        .style("display", 'none')
        .style('position', 'absolute')
        .style('z-index',0) // 設定z-index可以決定網頁的z軸，決定覆蓋的順序
        .attr("class", "tooltip2")
        .style("background-color", "white")
        .style("border", "solid")
        .style("border-width", "2px")
        .style("border-radius", "5px")
        .style("padding", "5px")
        .attr('id','tooltips2');

    var svg = d3.select("#svg_container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    var xScale = d3.scaleLinear()
        .domain([0, seqLength])
        .range([30, width - 30]);
    
    var inputSeq = svg.append("g")
        .attr("transform", "translate(0, 110)")
        .call(d3.axisBottom(xScale));
    
    inputSeq.selectAll("rect")
        .data(seqTable)
        .enter()
        .append("rect")
        .attr("x", function (d) { return xScale(d.start_point); })
        .attr("y", -20)
        
        .attr("width", function (d) { 
            return xScale(d.end_point) - xScale(d.start_point); })
        .attr("height", 15)
        .style("fill", function (d) { 
                if (d.type ==="UTR"){return "grey";}
                else{return "green";}
             })

        .on("mouseover", function (d) {

        })

        .on("mouseout", function (d) {
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });

    var piRNA = svg.append("g")
        .attr("transform", "translate(0, 110)")
        .call(d3.axisBottom(xScale));
    piRNA.selectAll("rect")
        .data(piRNA_Location)
        .enter()
        .append("rect")
        .attr("x", function (d) { return xScale(d.start_point); })
        .attr("y", function (d) {
            if (d.height_level === 0){return -45;}
            else if (d.height_level === 1){return -70;}
            else if (d.height_level === 2){return -95;}
            else if (d.height_level === 3){return -120;}
        })
        .attr("width", function (d) { 
            return xScale(d.end_point) - xScale(d.start_point); })
        .attr("height", 22)
        .style("fill", "red");

    d3.selectAll("text").style("font-size", "16px");
        };
window.onload = function(){
    callPython()
        .then(Response => {
            if (!Response.ok) {
                throw new Error("Response was not ok!");
            }
            return Response.json();
        })
        .then(Data => {
            loadDatatable(Data["piRNA"], "data_table");
            drawScaleLinear(Data["sequence"].length, Data["input Seq table"], Data["location_Table"]);

        })
}

