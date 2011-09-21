#pragma strict

var skin : GUISkin;

@HideInInspector var myUid : String;
@HideInInspector var hisUid : String;

function Start() {
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
	
	GetComponent.<Drawer>().enabled = true;
}

function OnGUI() {
	GUI.skin = skin;
	GUI.Label(Rect(0, 0, Screen.width, 100), hisUid ? hisUid : "waiting");
}
