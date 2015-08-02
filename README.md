#Programmer (looking for an awesome name)

ERPNext Projects for ERPNext programmers

## Motivation

I'm a programmer, I work with ERPNext, but not only with it, I have accounts in 

 - ERPNext (Ofcourse)
 - Bitbucket
 - Github
 - Wakatime
 - Email
 - Facebook
 - Twitter
 - And a lot of others tool that I use in my work

And my time is precious, I dont have time to collect my `Time Logs` in all tools, so the main focus of this project is:

Turn easy get data from API's that support oAuth.

## How ?

### APP Token

The first objective is turn easy add new oAuth API's in this

For this I designed `APP Token`

![APP Token](https://raw.githubusercontent.com/MaxMorais/programmer/master/help_images/APP Token.png)

`APP Token` can consume various oAuth API's, but for this, it have a requirement, do you will need register an APP in the data provider.

#### APP Token Parameters

![APP Token Parameters](https://raw.githubusercontent.com/MaxMorais/programmer/master/help_images/APP Token Params.png)

Using `APP Token Parameters` there you can add in a easy way `header`, `request` and `session` parameters

`APP Token Parameters` allow, for now, 2 shortcuts for variables.

 - *:user* that will be replaced for the user id
 - *:auth_code* that will be replaced for the authorization token given by a user

### Data Parser

The second objective is turn easy parse data from the API.

For this I designed `Data Parser`, you can use `Data Binds` for parse the data from an `endpoint`

![Data Parser](https://raw.githubusercontent.com/MaxMorais/programmer/master/help_images/Data Parser.png)

`Data Parser` can parser `JSON` and `XML` using `JSONPath` and `XPath`
 
#### Data Bind

`Data Bind` is used inside a `Data Parser` for map the relation of a (X|JSON)Path with the fields of a doctype.
But it is not a rule.

![DataBind](https://raw.githubusercontent.com/MaxMorais/programmer/master/help_images/Data Bind.png)



#### JSONPath and XPath Help

![XPath and JSONPath Help](https://raw.githubusercontent.com/MaxMorais/programmer/master/help_images/JSONPath and XPath Help.png)
