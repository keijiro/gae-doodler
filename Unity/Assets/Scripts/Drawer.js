#pragma strict

var appUrl : String = "http://gaedoodler.appspot.com/";

var myUid : String;
var hisUid : String;

var brushPrefab : GameObject;
var strokeLength = 256;

private var prevPoint = Vector3(-999, -999);
private var myStroke : Array = new Array();
private var hisStroke : Array = new Array();

function Start() {
	StartCoroutine(SendDataCoroutine());
	StartCoroutine(RecvDataCoroutine());
}

function Update() {
	if (Input.GetMouseButton(0)) {
		var point = ScreenToWorldPoint(Input.mousePosition);
		if ((prevPoint - point).magnitude > 0.02) {
			var brush = Instantiate(brushPrefab, point, Quaternion.identity) as GameObject;
			myStroke.Add(brush);
			if (myStroke.length >= strokeLength) Destroy(myStroke.shift());
			prevPoint = point;
		}
	}
}

function SendDataCoroutine() : IEnumerator {
	while (true) {
		var form = new WWWForm();
		form.AddField("uid", myUid);
		form.AddField("data", SerializeStroke(myStroke));
		
		var www = new WWW(appUrl + "set", form);
		yield www;

		yield WaitForSeconds(1.0);
	}
}

function RecvDataCoroutine() : IEnumerator {
	while (true) {
		var form = new WWWForm();
		form.AddField("uid", hisUid);
		
		var www = new WWW(appUrl + "get", form);
		yield www;

		if (www.text != "none") {
			DeserializeStroke(www.text);
		}

		yield WaitForSeconds(1.0);
	}
}

private function ScreenToWorldPoint(point : Vector3) : Vector3 {
	point -= Vector3(0.5 * Screen.width, 0.5 * Screen.height);
	return point * (2.0 / Screen.height);
}

private function SerializeStroke(stroke : Array) : String {
	if (stroke.length == 0) return "";
	var text = "";
	for (var brush : GameObject in stroke) {
		text += SerializePoint(brush.transform.position) + ",";
	}
	return text.Remove(text.length - 1);
}

private function SerializePoint(point : Vector3) : String {
	var x = Mathf.FloorToInt((point.x + 100.0) * 100);
	var y = Mathf.FloorToInt((point.y + 100.0) * 100);
	return ((x & 0xffff) + (y << 16)).ToString();
}

private function DeserializePoint(data : String) : Vector3 {
	var raw = int.Parse(data);
	var x = 0.01 * (raw & 0xffff) - 100.0;
	var y = 0.01 * (raw >> 16   ) - 100.0;
	return Vector3(x, y);
}

private function DeserializeStroke(text : String) {
	for (var brush : GameObject in hisStroke) {
		Destroy(brush);
	}
	
	hisStroke = new Array();
	
	for (var data in text.Split(","[0])) {
		var point = DeserializePoint(data);
		var brush = Instantiate(brushPrefab, point, Quaternion.identity) as GameObject;
		hisStroke.Add(brush);
	}
}
