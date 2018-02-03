$(document).ready(function(){
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});

$('#btn-est-param').click(function(){
    var pd = $('#pd').val();
    var evaluationPoint = $('#evaluation-point').val();
    console.log(evaluationPoint);
    var data = JSON.parse(dataStr);
    var useData = [];
    useData[0] = data[0].slice(0, evaluationPoint);
    useData[1] = data[1].slice(0, evaluationPoint);
    useData[2] = data[2].slice(0, evaluationPoint);
    useData[3] = data[3].slice(0, evaluationPoint); 
     
    $.ajax({
        url: 'ajax/test',
        data: {
            'data': JSON.stringify(useData),
            'pd': pd,
            'budget': data[1][data[1].length-1]
        },
        method: 'GET',
        contentType: "application/json; charset=utf-8",
        success: function(data){
            console.log(data.alpha);
            $('#alpha').val(data.alpha);
            $('#beta').val(data.beta);
            $('#gamma').val(data.gamma);            
        }
    })
})
