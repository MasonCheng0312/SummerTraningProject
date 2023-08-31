function callViewsForTransData(){
    var currentUrl = window.location.href;
    var targetUrl = currentUrl.replace("/detail_data/","/getData/")
    return fetch(targetUrl)        
};


function loadData(Data){//Data為一json檔
    

}



window.onload = function() {
    callViewsForTransData()
        .then(Response => {
            if(!Response.ok){
                throw new Error("Response was not ok!");
            }
            return Response.json();
        })
        .then(Data =>{

        })
        .catch(error => {
            console.error("There was some error in fetch operation :", error);
            throw error;
        });


};


