var crollNow = 0;

var followScroll = 1;
var stop = 0;
var ifbottom = 0;

var windowobject;

var windowHeight;

var SmoothScroll = function(win, opt) {
	//操作对象
	this.win = win;
	this.timeStamp = new Date().getTime();
	//每次滚动位移
	this.step = opt ? opt.step || 400 : 400;
	//缓动系数
	this.f = opt ? opt.f || 0.06 : 0.06;
	this.interval = 10;
	this.intervalID = null;
	this.isFF = navigator.userAgent.toLowerCase().indexOf("firefox") >= 0;
	this.upOrDown = "";
	this.init();
};
var i = 0;
SmoothScroll.prototype = {

	init : function() {
		var _this = this;

		if (_this.isFF) {
			_this.win.addEventListener('DOMMouseScroll', function(e) {

				_this.upOrDown = e.detail < 0 ? "up" : "down";
				_this.scrollHander();

				if (e.preventDefault)
					e.preventDefault();
				else
					return false;
			}, false);
		}else {
			_this.win.onmousewheel = function(e) {
				e = e || window.event;
				_this.upOrDown = e.wheelDelta > 0 ? "up" : "down";
				_this.scrollHander();

				if (e.preventDefault)
					e.preventDefault();
				else
					return false;
			};
		}
	},
	scrollHander : function() {
		var _this = this;
		var _step = _this.step * (_this.upOrDown == "up" ? -1 : 1);
		var tar = $(window).scrollTop() + _step;
		if (tar < $("body").height() - 10) {
			if (!$(windowobject).is(":animated")) {//避免多次滚轮造成的多次滚动

				$(windowobject).animate({
					"scrollTop" : "+=" + _step + "px"
				}, 600, function() {
					if (_this.upOrDown == "up") {//代表转轮往上，文本内容其实是往下
						crash_bottom(1, $(window).scrollTop(), 20, 150);
					} else {
						crash(0, $(window).scrollTop(), 20, 150);
					}

				});
				if ($(window).scrollTop() <= _this.step && _this.upOrDown == 'up') {
					
				}else {
					$('#guider').animate({
						// "top" : tar + (_this.step - $('#guider').height()) /2
						"top" : tar + (_this.step - $('#guider').height())/1.1
					}, 800, function() {
						var index = Math.round(tar / windowHeight);
					});
				}
			}

		}

	}
};

function backToTop() {
	$(windowobject).animate({
		"scrollTop" : "0px"
	}, 1700, function() {

	});
}

function linkToPage(index) {
	if (!$(windowobject).is(":animated")) {
		index = parseInt(index);
		if ($(".stage").eq(index).offset().top > $("body").scrollTop()) {
			$(windowobject).animate({
				"scrollTop" : $(".stage").eq(index).offset().top + "px"
			}, 1000, function() {
				crash(0, $(".stage").eq(index).offset().top, 20, 150);
			});
		} else {
			$(windowobject).animate({
				"scrollTop" : $(".stage").eq(index).offset().top + "px"
			}, 1000, function() {
				crash_bottom(1, $(".stage").eq(index).offset().top, 20, 150);
			});
		}
		if (index !== 0) {
			// var height = $(".stage").eq(index).offset().top + windowHeight / 2 - $("#guider").height() / 2;
			var height = $(".stage").eq(index).offset().top + windowHeight - $("#guider").height()*2;
			$("#guider").animate({
				"top" : height + 20 + "px"
			}, 1000);
		}
	}
}

function crash_bottom(direction, termin, distant, time) {
	if (!stop) {
		var scrollTop = $(window).scrollTop();
		if (direction == 1) {//向上
			direction = 0;
			$(windowobject).animate({
				"scrollTop" : "+=" + distant + "px"
			}, time, function() {
				crash_bottom(direction, termin, distant * 0.6, time);
				if (distant <= 15 || time > 150) {
					stop = 1;
					//代表开始停止碰撞

					$(windowobject).animate({
						"scrollTop" : termin + "px"
					}, time, function() {
						//为0代表碰撞结束
						crollNow = termin;
						stop = 0;
					});
				}
			});
		} else if (direction == 0) {//向下
			direction = 1;
			$(windowobject).animate({
				"scrollTop" : termin + "px"
			}, time, function() {
				crash_bottom(direction, termin, distant * 0.6, time);
				if (distant <= 15 || time > 150) {
					stop = 1;
					$(windowobject).animate({
						"scrollTop" : termin + "px"
					}, time, function() {
						crollNow = termin;
						stop = 0;
					});
				}
			});

		}
	}
}

function crash(direction, termin, distant, time) {
	if (!stop) {
		var scrollTop = $(window).scrollTop();
		if (direction == 0) {//向下
			direction = 1;
			$(windowobject).animate({
				"scrollTop" : "-=" + distant + "px"
			}, time, function() {
				crash(direction, termin, distant * 0.6, time);
				if (distant <= 15 || time > 150) {
					stop = 1;
					$(windowobject).animate({
						"scrollTop" : termin + "px"
					}, time, function() {
						crollNow = termin;
						stop = 0;
					});
				}
			});
		} else if (direction == 1) {//向上
			direction = 0;
			$(windowobject).animate({
				"scrollTop" : termin + "px"
			}, time, function() {
				crash(direction, termin, distant * 0.6, time);
				if (distant <= 15 || time > 150) {
					stop = 1;
					$(windowobject).animate({
						"scrollTop" : termin + "px"
					}, time, function() {
						crollNow = termin;
						stop = 0;
						setTimeout(function() {
							if (!ifbottom) {
								followScroll = 1;
							}
						}, 100);
					});
				}
			});
		}
	}
}

var topwin = 1;

function signAnimate() {
	var cicleFun = function(name1, name2, name3, shift, interval) {
		$(name1).animate({
			"bottom" : "-=" + shift + "px"
		}, interval, function() {
			$(name1).hide();
			$(name2).animate({
				"bottom" : "-=" + shift + "px"
			}, interval, function() {
				$(name2).hide();
				$(name3).animate({
					"bottom" : "-=" + shift + "px"
				}, interval, function() {
					$(name3).hide();
					$(name1).css("bottom", "+=" + shift * 2 + "px").show().animate({
						"bottom" : "-=" + shift + "px"
					}, interval, function() {
						$(name2).css("bottom", "+=" + shift * 2 + "px").show().animate({
							"bottom" : "-=" + shift + "px"
						}, interval, function() {
							$(name3).css("bottom", "+=" + shift * 2 + "px").show().animate({
								"bottom" : "-=" + shift + "px"
							}, interval, function() {
								setTimeout(function() {
									cicleFun(name1, name2, name3, shift, interval)
								}, 1500);
							});
						});
					});
				});
			});
		});
	};
	cicleFun("#sign1_1", "#sign2_1", "#sign3_1", 30, 200);
	cicleFun("#sign1_2", "#sign2_2", "#sign3_2", 30, 200);
	cicleFun("#sign1_plus", "#sign2_plus", "#sign3_plus", 30, 200);
	cicleFun("#sign1_3", "#sign2_3", "#sign3_3", 30, 200);
	cicleFun("#sign1_4", "#sign2_4", "#sign3_4", 30, 200);

}

if (!('placeholder' in document.createElement('input'))) {
	$('input[placeholder]').each(function() {
		var that = $(this), text = that.attr('placeholder');
		if (that.val() === "") {
			that.val(text).addClass('placeholder');
		}
		that.focus(function() {
			if (that.val() === text) {
				that.val("").removeClass('placeholder');
			}
		}).blur(function() {
			if (that.val() === "") {
				that.val(text).addClass('placeholder');
			}
		}).closest('form').submit(function() {
			if (that.val() === text) {
				that.val('');
			}
		});
	});
}
$(document).ready(function() {
	var is_chrome = navigator.userAgent.toLowerCase().indexOf('chrome') > -1;
	var is_safari = navigator.userAgent.toLowerCase().indexOf("safari") > -1;
	if (is_chrome || is_safari) {
		//判断是chrome、safari, 供scrollTop兼容性使用
		windowobject = "body";
	}else {
		//支持ie和ff
		windowobject = "html";
	}
	if(is_chrome){
		var timer = setInterval(function(){
			 if($('input:-webkit-autofill').html()!=undefined){
				$('input:-webkit-autofill').each(function(){
			      $(this).before(this.outerHTML).remove();
			    });
			    clearInterval(timer);
			 }
		},10);
	}
	
	$(".index_link").click(function() {
		var index = parseInt($(this).attr("index"));
		$(".index_link").eq(index).addClass("select");
		linkToPage(index);
	});
	backToTop();
	$(".mail").trigger("focus");
	//当前窗口大小
	windowHeight = document.documentElement.clientHeight;

	$(".stage").css("height", windowHeight);
	//$("#guider").css("top", $("body").height() - windowHeight / 2 - $("#guider").height() / 2);
	$("#guider").css("top", $("body").height() - windowHeight / 6 - $("#guider").height() / 5);
	var opt = {
		step : windowHeight,
		f : 1
	};
	var div = document.body;
	new SmoothScroll(div, opt);

	//窗口大小变化时，触发每个屏幕大小变化
	var resizeHandler = function() {
		$("body").stop(true, true);
		//阻止碰撞
		stop = 1;
		windowHeight = document.documentElement.clientHeight;

		$(".stage").css("height", windowHeight);
		//$("#guider").css("top", $("body").height() - windowHeight / 2 - $("#guider").height() / 2);
		$("#guider").css("top", $("body").height() - windowHeight / 6 - $("#guider").height() / 5);
		var opt = {
			step : windowHeight,
			f : 1
		};
		var div = document.body;
		new SmoothScroll(div, opt);
		var index = Math.floor($(window).scrollTop() / windowHeight);
		$(windowobject).animate({
			"scrollTop" : index * windowHeight + "px"
		});
		if (index != 0) {
			// var tmpheight = index * windowHeight + (windowHeight - $("#guider").height()) / 2;
			var tmpheight = index * windowHeight + (windowHeight - $("#guider").height()) / 1.1;
			$("#guider").animate({
				"top" : tmpheight
			}, 0);
		}
		//300毫秒后执行stop=0,目的是保证ie下crash函数（也是timer）执行完。
		setTimeout(function() {
			stop = 0;
		}, 300);
	};
	$(window).resize(function() {
		setTimeout(resizeHandler, 10);
	});

	signAnimate();

	$('#guider').on('click', backToTop);
	$('#logintab').addClass('crt');
	$('.j-ok').css('background-position', '-499px -783px');
	$('.j-ok').attr('data-checked', "1");

	function focusOrBlur(id){
		id.focus(function(){
	        eduitBtnText();      
		}).blur(function(){
	        eduitBtnText();
		});
	}
	function eduitBtnText(){
		var txt = $('#loginsubmit span').text();
		if(txt == '用户名或密码错误' || txt == '请输入用户名' || txt == '请输入密码'){
        	$('#loginsubmit span').text('登录');
        } 
	}
	setInterval(function(){
		focusOrBlur($(".mail"));
		focusOrBlur($(".password"));
	},1000);
	
	//check input
	function check() {
		var username = $("#username").val();
		var password = $("#password").val();
		if (username == "") {
			//$("#username").focus();
			$('#loginsubmit span').text('请输入用户名');
			return false;
		}
		if (password == "") {
			//$("#password").focus();
			$('#loginsubmit span').text('请输入密码');
			return false;
		}
		return true;
	}

	function login() {
		$.ajax({
			type : "POST",
			url : "/auth/ajax_login",
			data : {
				nickname : $("#username").val(),
				password : $("#password").val()
			},
			dataType : "json",
			success : function(data) {
				if (data.code == 200) {
					location.href = data.url;
					$('#loginsubmit span').text("登录中");
					//setTimeout("window.location='"+data.url+"';",1000);
				} else {
					$('#loginsubmit span').text('用户名或密码错误');
					return false;
				}

			}
		});
	}

	//login and download pages change
	var dom = $('.userlnks').children();
	$('.userlnks a').on('click', function(e) {
		if ($(e.target).text() == '登录') {
			$(dom[0]).addClass('crt');
			$(dom[1]).removeClass('crt');
			$('#newlogin').show();
			$('#newregister').hide();
		} else if ($(e.target).text() == '注册') {
			$(dom[1]).addClass('crt');
			$(dom[0]).removeClass('crt');
			$('#newlogin').hide();
			$('#newregister').show();
		}
	});
	//remember username and password
	$('.j-ok').on('click', function() {
		var checked = $(this).attr('data-checked');
		if (checked == "0") {
			$(this).css('background-position', '-499px -783px');
			$(this).attr('data-checked', "1");
		} else {
			$(this).css('background-position', '');
			$(this).attr('data-checked', "0");
		}
	});
	//submit
	$("#loginsubmit").click(function() {
		event.preventDefault();
		if (check()) {
			login();
		}
	});
	//enter
	$(document).on('keydown', function() {
		var e = e || event;
		var currKey = e.keyCode || e.which || e.charCode;
		if (currKey == 13) {
			if (check()) {
				login();
			}
		}
	});
}); 
