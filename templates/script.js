/* ---- layout.html ----*/
let day = new Date();

/* ----- home.html ----- */      
let resident_id = ''
let resident_name = ''
let space_name = ''
let go_out = ''
let today = ''
let lastClickedButton = null;
let staff_name = {{login_staff[1]|tojson}}
// 現在の日時を取得
let now = new Date();
// 年月日時分を2桁表示にしてフォーマット
let year = now.getFullYear();
let month = ('0' + (now.getMonth() + 1)).slice(-2);
let day_data = ('0' + now.getDate()).slice(-2);
let hours = ('0' + now.getHours()).slice(-2);
let minutes = ('0' + now.getMinutes()).slice(-2);
let currentMonth = year + '-' + month //年月
let currentDate =  year + '-' + month + '-' + day_data //年月日
let currentDateTime = year + '-' + month + '-' + day_data + ' ' + hours + ':' + minutes + ':00'; //年月日時
//月の最初の日付を取得
let firstDay = new Date(year, month - 1, 1);
// 月の最終日を取得
let lastDay = new Date(year, month, 0);

/* --------  index.html  -------- */
let flask_day = new Date({{day_value|tojson}});

function make_day(day) {
	day.setDate(day.getDate());
	let yyyy = day.getFullYear();
	let mm = ('0' + (day.getMonth() + 1)).slice(-2);
	let dd = ('0' + day.getDate()).slice(-2);
	return yyyy + '-' + mm + '-' + dd;
}

flask_day = make_day(flask_day)

/* ---- mail.html ---- */      
