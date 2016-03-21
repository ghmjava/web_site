var option_base = {
            title : {
                text: '',
                subtext: '',
                x: 'center'
            },
            tooltip : {
                trigger: 'axis'
            },
            toolbox: {
                show : true,
                feature : {
                    mark : {show: true},
                    dataView : {show: true, readOnly: false},
                    restore : {show: true},
                    saveAsImage : {show: true}
                }
            },
            
            xAxis : [
                {
                    type : 'category',
                    boundaryGap : false,
                    data : [] //
                },
                {
                    type : 'value',
                    scale : true,
                    //splitNumber: 29,
                    axisLabel: {show:false},
                    splitLine: {show:false}
                }
            ],
            yAxis : [
                {
                    type : 'value'
                },
                {
                    type : 'value'
                }
            ],
            animation: false,
            series : [
                {
                    name:'散点',
                    type:'scatter',
                    
                    //yAxisIndex:1,
                    //xAxisIndex:1,
                    symbol: 'circle',
                    symbolSize: 5,
                    data: [] //
                },
                {
                    name:'折线',
                    type:'line',
                    data: [] //
                }
            ]
        };                




function get_algo_save_scene_record(source_table, module_id, scene_id, record_id, if_only_save_record, if_can_write){
    var current_record_id = arguments[3] ? arguments[3] : 0;
    var if_can_write = arguments[5] ? arguments[5] : 1;
    if(if_only_save_record){
        var if_only_save_record = if_only_save_record
    } else{
        var if_only_save_record = false
    }

    var names = []
    var all_inputs = $("#" + source_table + " input");
    var dict = {}
    for(var i=0;i<all_inputs.length;i++){
        if ( names.indexOf(all_inputs[i].name) == -1)
        {
            //if(all_inputs[i].name.search("#api#") == -1){ // 过滤掉
            names.push(all_inputs[i].name);
            //}
        }
    }

    for(var n=0;n < names.length;n++){
        dict[names[n]] = []
        var tmp = $("#" + source_table + " input[name='" + names[n] + "']")
        for(var t=0; t < tmp.length;t++){
            if(tmp[t].value != ""){
                dict[names[n]].push(tmp[t].value)
            }
        }
    }

    if(if_only_save_record){
        record_name = $("#new_record_name")[0].value
    }else{
        record_name = $("#" + record_id + "_record_name")[0].value

    }
    //console.log(dict);
    //save record
    var y = dict['total']

    if(if_can_write == 1){
        if (current_record_id != 0){
            var record_id = save_scene_record(module_id, scene_id, dict, current_record_id, record_name).responseJSON
            record_id = current_record_id
        }else{
            var record_id = save_scene_record(module_id, scene_id, dict, 0 , record_name).responseJSON
        }   
    }else{
        var record_id = record_id
        //alert("您没有写权限");
    }
    

    if (if_only_save_record){
        location.reload();
    }else{
        delete dict['total']
        // send request to get algorithm based on given x y


        for(k in dict){
            if (k.search('#api#') == -1){
                if(dict[k].length < 2 ){
                    alert('请至少提供两条数据');
                    break;
                }else{
                    if (current_record_id == 0){
                        dd = set_algo('new' + "_" + k, dict[k], y, scene_id, module_id, record_id, k).responseJSON
                    }else{
                        dd = set_algo(record_id + "_" + k, dict[k], y, scene_id, module_id, record_id, k).responseJSON
                    }
                }
                
            }   
        }
    }
}



function save_scene_record(module_id, scene_id, data, record_id, record_name){
    var current_record_id = arguments[3] ? arguments[3] : 0;
    var post_data = {}
    post_data['module_id'] = module_id
    post_data['scene_id'] = scene_id
    post_data['data'] = data
    post_data['record_name'] = record_name
    if(current_record_id != 0){
        post_data['id'] = current_record_id
    }
    return $.post(
        "/assess_mgr/save/scene_record",
        JSON.stringify(post_data),
        function(data,status){
            if(status == 'success'){
                alert('save scene_record success')
            }else{
                alert('save scene_record fail')
            }
        }
    );
}


function set_algo(div_id , x, y, scene_id, module_id, record_id, resource_name){ // div id = {{record_id}}_{{resouce_name}}
    var post_data = {}
    post_data['x'] = x
    post_data['y'] = y
    post_data['scene_id'] = scene_id
    post_data['module_id'] = module_id
    post_data['id'] = record_id
    post_data['resource'] = resource_name
    var ret;
    var Echarts;
    require(
            [
                'echarts',
                'echarts/chart/line',
                'echarts/chart/scatter',
            ],
            function (ec){
                Echarts = ec
            }
    );
    return $.post(
        "../assess_mgr/get/algo",
        JSON.stringify(post_data),
        function(data,status){
            if(status == 'success'){
                $("#" + div_id).css('display',"block")
                set_chart(div_id, data.data,Echarts);              
            } 
        }

    );

}

function set_chart(div_id, data, Echarts){
    
    var this_option = option_base
    this_option.xAxis[0].data = data.xaxis
    this_option.series[0].data = data.scatter
    this_option.series[1].data = data.line
    this_option.title.text = div_id.split('_')[1]
    this_option.title.text += " - 总tps"
    this_option.title.subtext = "公式 Y = " + data.a + '*X + ' + data.b;
    
    /*
    require(
        [
            'echarts',
            'echarts/chart/line',
            'echarts/chart/scatter',
        ],
        function(ec){
            var mychart = null; 
            mychart = ec.init(document.getElementById(div_id));
            console.log('real div_id:', div_id)
            console.log(this_option)
            mychart.setOption(this_option)
            mychart = null

        }
    );*/
    
    var mychart = null; 
    mychart = Echarts.init(document.getElementById(div_id));
    mychart.setOption(this_option)
    mychart = null

    //console.log('set_chart',this_option);

}




function delete_record(record_id){
    return $.post(
        '/assess_mgr/delete/scene_record',
        JSON.stringify({'id':record_id}),
        function (data, status){
            if(status == 'success'){
                alert('删除成功！');
                location.reload()
            }
        }
        );
}


function add_line(this_item, table_id){
    this_item.onclick = function(){this.parentNode.parentNode.remove()};
    this_item.classList.remove("btn-success")
    this_item.classList.add("btn-danger")
    this_item.textContent = '删除'

    //var tbody = $("#" + table_id + " tbody")[0]

    var tbody = $("#" + table_id + "_body")
    var new_line = $("#" + table_id + " tr[name=new_line_tr]").clone()
    for(var i;i<new_line.find('input').length;i++){
        new_line.find('input')[i].value='';
    }

    // change accordion-group info
    var current_toggle_href = new_line.children().children().children().children()[0].href 
    var new_id = "accordion" + String(Math.random()*10000).substr(0,4)
    new_line.children().children().children()[1].id = new_id  //set new id for accordion heading
    new_line.children().children().children().children()[0].href =  "#" + new_id //change toggle href as accordion id
    new_line.css("display","")   
    new_line.attr('name','');

    tbody.append(new_line);

}

/*
function add_line(this_item,table_id){
    console.log(this_item);
    this_item.onclick = function(){this.parentNode.parentNode.remove()};
    this_item.classList.remove("btn-success")
    this_item.classList.add("btn-danger")
    this_item.textContent = '删除'

    var tbody = $("#" + table_id + " tbody")
    var new_line = $("#" + table_id + " tr[name=new_line_tr]").clone()
    for(var i;i<new_line.find('input').length;i++){
        new_line.find('input')[i].value='';
    }
    new_line.css("display","")   
    new_line.attr('name',''); 
     
    tbody.append(new_line);
    console.log(new_line.name)
}
*/

function delete_line(this_tr){
    this_tr.parentNode.parentNode.remove()
}


function auto_fill_by_ratio(this_item){
    var temp_id = String(Math.random()*100000).substr(0,5)
    this_item.parentElement.parentElement.id = temp_id
    var all_inputs = $("#" + temp_id).find("input")
    var total = null;
    for(var i=0;i<all_inputs.length;i++){
        if(all_inputs[i].name == 'total')
        {
            var total = all_inputs[i].value
        }
    }
    for(var i=0;i<all_inputs.length;i++){
        if(all_inputs[i].name.search('#api#') == 0 && total){
            ratio = all_inputs[i].attributes['ratio'].value
            all_inputs[i].value = total/100*ratio
        }
    }
    /*
    var tds = this_item.parentElement.parentElement.children
    for(var i=0;i<tds.length;i++){
        if (tds[i].children[0].name.search('#api#') != -1) {
            this_ratio = tds[i].children[0].attributes['ratio'].value;
            console.log(tds[i].children[0].name, this_ratio)
            this_value = this_ratio/100 * this_item.value;
            console.log(this_value)
            tds[i].children[0].value = this_value
        };
    }
    */

    $("#" + temp_id).removeAttr("id")

}




function auto_cal_ratio(this_item){
    var tds = this_item.parentElement.parentElement.children;
    var total_value;
    for(var i=0;i<tds.length;i++){
        if(tds[i].children[0].name == 'total'){
            total_value = tds[i].children[0].value
        }
    }

    ratio = this_item.value / total_value * 100
    this_item.parentElement.appendChild($('<small style="float:right;color:gray">占总tps ' + ratio+ '%</small>')[0])
}


function choose_formula(module_id,scene_id,record_id){
    var post_data = {}
    post_data['module_id'] = module_id
    post_data['scene_id'] = scene_id
    post_data['record_id'] = record_id

    $.post(
        "/assess_mgr/estimate",
        JSON.stringify(post_data),
        function(data,status){
            if(status == 'success'){
                console.log('choose_formula', data.data)
                if(data.data.tps == null){
                    $("#" + record_id + "_choose_formula").removeClass('alert-success').addClass("alert-danger")
                    $("#" + record_id + "_choose_formula").html("还没有生成函数，请点击‘生成函数’");

                }else{
                    $("#" + record_id + "_choose_formula").html("预估最大tps为: " + data.data.tps + " 性能瓶颈为: " + data.data.resource_name)
                }
            } 
        }

    );
}


function change_child_value_by_name(item, item_name, value){
    children = item.children
    for(var i =0;i<children.length;i++){
        if(children[i].name.search(item_name)){
            children[i].value = value
        }
        if(children[i].children.lengh != 0){
            change_child_attr_by_name(children[i], item_name, value)
        }
    }
}