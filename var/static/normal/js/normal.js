
//获取select选项的值
function getSelectValues(obj_id){
    var selectedValues = "";
    var selectObject = document.getElementById(obj_id);
    for(var i=0; i<selectObject.options.length; i++){
        if(selectObject.options[i].selected == true){
            selectedValues += selectObject.options[i].value + ',';
        }
    }
    selectedValues = selectedValues.substring(0, selectedValues.lastIndexOf(','));
    return selectedValues
}

//根据name获取checkbox值列表
function get_checkbox_value(name){
    var arrChk=$("input[name='"+ name +"']:checked");
    var value_list=[];
    for (var i=0;i<arrChk.length;i++)
    {
      value_list.push(arrChk[i].value)
    }
    return value_list
}

//通过POST异步提交json数据
function post(url, json_data){
  $.post(url,
    JSON.stringify(json_data),
    function(data,status){
      if(data.status == "success"){
        alert("操作成功，页面将会自动刷新！")
        window.location.href=window.location.href;
      }else{
        alert("操作失败！"+data.message)
      }
  });
}