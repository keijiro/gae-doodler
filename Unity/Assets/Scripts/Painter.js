#pragma strict

var brushPrefabs : GameObject[];
var strokeLength = 256;

private var myUid : String;
private var hisUid : String;

private var prevPoint = Vector3(-999, -999);

private var myStroke : Array = new Array();
private var hisStroke : Array = new Array();

function SetUids(myUid : String, hisUid : String) {
	this.myUid = myUid;
	this.hisUid = hisUid;
}

function Start() {
	StartCoroutine(SendDataCoroutine());
	StartCoroutine(RecvDataCoroutine());
}

function Update() {
	if (Input.GetMouseButton(0)) {
		var point = ScreenToWorldPoint(Input.mousePosition);
		if ((prevPoint - point).magnitude > 0.02) {
			var brush = Instantiate(brushPrefabs[0], point, Quaternion.identity) as GameObject;
			myStroke.Add(brush);
			if (myStroke.length >= strokeLength) Destroy(myStroke.shift() as GameObject);
			prevPoint = point;
		}
	}
}

function OnDestroy() {
	for (var brush : Object in myStroke) Destroy(brush as GameObject);
	for (var brush : Object in hisStroke) Destroy(brush as GameObject);
}

function SendDataCoroutine() : IEnumerator {
	while (true) {
		var form = new WWWForm();
		form.AddField("uid", myUid);
		form.AddField("data", SerializeStroke(myStroke));
		
		var www = new WWW(Config.appUrl + "update", form);
		yield WaitForSeconds(Config.requestInterval);
		yield www;
	}
}

function RecvDataCoroutine() : IEnumerator {
	while (true) {
		var form = new WWWForm();
		form.AddField("uid", hisUid);
		
		var www = new WWW(Config.appUrl + "stroke", form);
		yield WaitForSeconds(Config.requestInterval);
		yield www;
		
		if (www.text == "invalid") {
			Destroy(gameObject);
			break;
		}

		if (www.text != "none") DeserializeStroke(www.text);
	}
}

private function ScreenToWorldPoint(point : Vector3) : Vector3 {
	point -= Vector3(0.5 * Screen.width, 0.5 * Screen.height);
	return point * (2.0 / Screen.height);
}

private function SerializeStroke(stroke : Array) : String {
	if (stroke.length == 0) return "";
	var text = "";
	for (var brush : Object in stroke) {
		text += SerializePoint((brush as GameObject).transform.position) + ",";
	}
	return text.Remove(text.length - 1);
}

private function SerializePoint(point : Vector3) : String {
	var x = Mathf.FloorToInt((point.x + 100.0) * 100);
	var y = Mathf.FloorToInt((point.y + 100.0) * 100);
	return ((x & 0xffff) + (y << 16)).ToString();
}

private function DeserializePoint(data : String) : Vector3 {
	var raw : int;
	if (int.TryParse(data, raw)) {
		var x = 0.01 * (raw & 0xffff) - 100.0;
		var y = 0.01 * (raw >> 16   ) - 100.0;
		return Vector3(x, y);
	} else {
		return Vector3.zero;
	}
}

private function DeserializeStroke(text : String) {
	for (var brush : Object in hisStroke) {
		Destroy(brush as GameObject);
	}
	
	hisStroke = new Array();
	
	for (var data in text.Split(","[0])) {
		var point = DeserializePoint(data);
		var brush = Instantiate(brushPrefabs[1], point, Quaternion.identity) as GameObject;
		hisStroke.Add(brush);
	}
}
