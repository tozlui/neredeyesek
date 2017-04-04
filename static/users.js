function hideFromUser(x)
{
	//0=admin, 1=registered_user 2=visitor
	if(x==0)
	{
		var x = document.getElementsByClassName("items-to-hide");
		var i=0;

		while(x[i])
		{
			x[i].style.visibility = "visible";
			i++;
		}
	}
	else if(x==1)
	{
		var x = document.getElementsByClassName("users-only");
		var i=0;

		while(x[i])
		{
			x[i].style.visibility = "visible";
			i++;
		}
	}

}

//window.onload = hideFromUser();