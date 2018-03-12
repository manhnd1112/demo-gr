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
    $('.form.upload-input .btn-load-data').click(function(e) {
        e.preventDefault();
        $('.form.upload-input input[type="file"]').click();
    })

    $('.form.upload-input input[type="file"]').change(function(){
        $('.form.upload-input').submit();
    })

    $('input:radio[name="project_evaluate"]').change(function(){
        var evaluation_time = parseFloat($(this).val());
        var pd = parseInt($('#pd').val());
        var evaluation_point = Math.round(evaluation_time*pd);
        $('#evaluation-point').val(evaluation_point);
    })
});



$('#btn-est-param').click(function(){
    var project_name = $('#project_name').text();
    var pd = $('#pd').val();
    var budget = $('#bac').val();
    var evaluationPoint = $('#evaluation-point').val();
    var evaluation_percent = parseFloat($('input[name="project_evaluate"]:checked').val())*100;
    var growModel = $('input[name=grow-model]:checked').val();
    console.log(growModel);
    var data = JSON.parse(dataStr);
    var useData = [];
    useData[0] = data[0];
    // PV
    useData[1] = data[1];
    // EV - PV
    useData[2] = data[2].slice(0, evaluationPoint).concat(data[1].slice(evaluationPoint, pd));
    // AC - PV
    useData[3] = data[3].slice(0, evaluationPoint).concat(data[1].slice(evaluationPoint, pd));
    // AC
    AC = data[3][data[3].length-1];
    console.log(AC);
    $.ajax({
        url: 'ajax/test',
        data: {
            'project_name': project_name,
            'data': JSON.stringify(useData),
            'pd': pd,
            'budget': budget,
            'evaluationPoint': evaluationPoint,
            'evaluation_percent': evaluation_percent,
            'growModel': growModel,
            'AC': AC
        },
        method: 'GET',
        contentType: "application/json; charset=utf-8",
        success: function(data){
            console.log(data);
            $('#alpha').val(data.alpha);
            $('#beta').val(data.beta);
            $('#gamma').val(data.gamma);     
            $('#ES').text(data.ES);
            $('#SPI').text(data.SPI);       
            $('#CPI').text(data.CPI);       
            $('#SPIt').text(data.SPIt);       
            $('#SCI').text(data.SCI);       
            $('#SCIt').text(data.SCIt);       
            $('#TV').text(data.TV);       
            $('#ED').text(data.ED);       
            $('#EACtPV1').text(data.EACtPV1);
            $('#EACtPV2').text(data.EACtPV2);
            $('#EACtPV3').text(data.EACtPV3);
            $('#EACtED1').text(data.EACtED1);            
            $('#EACtED2').text(data.EACtED2);            
            $('#EACtED3').text(data.EACtED3);
            $('#EACtES1').text(data.EACtES1);                        
            $('#EACtES2').text(data.EACtES2);                        
            $('#EACtES3').text(data.EACtES3);
            $('#EAC1').text(data.EAC1);                                                
            $('#EAC2').text(data.EAC2);                                                
            $('#EAC3-SPI').text(data.EAC3_SPI);                                                
            $('#EAC3-SPIt').text(data.EAC3_SPIt);    
            $('#EAC4-SCI').text(data.EAC4_SCI);                                                            
            $('#EAC4-SCIt').text(data.EAC4_SCIt);
            $('#EAC5-CI').text(data.EAC5_CI);                                                            
            $('#EAC5-CIt').text(data.EAC5_CIt);                                                                        
            $('#EAC-GM1').text(data.EAC_GM1);                                                                        
            $('#EAC-GM2').text(data.EAC_GM2);                                                                        
        }
    })
})

$('#btn-test').click(function(){
    var data = JSON.parse(dataStr);
    var pd = $('#pd').val();
    var budget = $('#bac').val();
    var alpha = parseFloat($('#alpha').val());
    var beta = parseFloat($('#beta').val());
    var gamma = parseFloat($('#gamma').val());
    var dataTest = parseInt($('#data-test').val());
    //a * np.exp(-np.exp(b - c*xdata))
    var resultTest = alpha * Math.exp(-Math.exp(beta - gamma*(data[0][dataTest-1]/pd)));
    var rightResult = data[3][dataTest-1]/budget;
    $('#result-test').text(resultTest+"");
    $('#right-result').text(rightResult);
})
