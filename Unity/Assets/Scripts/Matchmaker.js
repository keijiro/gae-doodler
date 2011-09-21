#pragma strict

var skin : GUISkin;
var painterPrefab : Painter;

private var myUid : String;
private var hisUid : String;

function Start() {
	while (true) {
		myUid = Random.Range(0, 0x7fffffff).ToString("X08");
		
		var form = new WWWForm();
		form.AddField("uid", myUid);
		
		var www = new WWW(Config.appUrl + "match", form);
		yield www;
		
		if (www.text != "wait") {
			hisUid = www.text;
		} else {
			while (true) {
				yield WaitForSeconds(0.5);
				
				www = new WWW(Config.appUrl + "mate", form);
				yield www;
				
				if (www.text != "none") {
					hisUid = www.text;
					break;
				}
			}
		}
		
		var painter = Instantiate(painterPrefab) as Painter;
		painter.SetUids(myUid, hisUid);
		
		while (painter) yield;
		
		www = new WWW(Config.appUrl + "quit", form);
		yield www;
		
		myUid = null;
		hisUid = null;
	}
}

function OnGUI() {
	GUI.skin = skin;
	GUI.Label(Rect(0, 0, Screen.width, 100), hisUid ? hisUid : "waiting");
}
