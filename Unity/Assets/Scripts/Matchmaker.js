#pragma strict

var skin : GUISkin;
var painterPrefab : Painter;

private var state : String;

private var myUid : String;
private var hisUid : String;

function Start() {
	while (true) {
		while (!state) yield;
		
		myUid = Random.Range(0, 0x7fffffff).ToString("X08");
		
		var form = new WWWForm();
		form.AddField("uid", myUid);
		
		var www = new WWW(Config.appUrl + "match", form);
		yield www;
		
		while (true) {
			yield WaitForSeconds(0.5);
			
			www = new WWW(Config.appUrl + "mate", form);
			yield www;
			
			if (www.text != "none") {
				hisUid = www.text;
				break;
			}
		}
		
		state = "matched";
		
		var painter = Instantiate(painterPrefab) as Painter;
		painter.SetUids(myUid, hisUid);
		
		while (painter && state == "matched") yield;
		if (painter) Destroy(painter.gameObject);
		
		www = new WWW(Config.appUrl + "quit", form);
		yield www;

		state = null;
		
		myUid = null;
		hisUid = null;
	}
}

function OnGUI() {
	GUI.skin = skin;
	
	var sw = Screen.width;
	var sh = Screen.height;
	
	var rect1 = Rect(0, 0, sw / 2, sh / 2);
	var rect2 = Rect(sw / 2, 0, sw / 2, 30);
	
	if (state == "ready") {
		GUI.Label(rect1, "Waiting...");
	} else if (state == "matched") {
		GUI.Label(rect1, "ID1:" + myUid + "\nID2:" + hisUid);
		if (GUI.Button(rect2, "Disconnect")) state = "quit";
	} else {
		GUI.Label(rect1, "Disconnected");
		if (GUI.Button(rect2, "Connect")) state = "ready";
	}
}
