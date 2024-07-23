#include <LiquidCrystal_I2C.h>
#include <string.h>

/*
 * DEFINE SECTION 
 */
 
#define PIN_BUZZ 9
#define PIN_BUTST 4
#define PIN_BUTMOD 7
#define PIN_BUTACT 2
#define PIN_BUTORDER 3
#define PIN_BUTINC 13
#define PIN_BUTDEC 10
#define GREEN_LED 12
#define RED_LED 8
/*
 * LCDs addresses
 */
#define LCD1 0x22
#define LCD2 0x27
#define LCD3 0x23

#define BRATE 9600
#define MAX_MSG_LGT 40 // 40 is actually too much, but just for safety let's keep it
#define MAX_MODS 3
/*
 * GLOBAL VARIABLES
 */

LiquidCrystal_I2C lcd(LCD1, 16, 2);
LiquidCrystal_I2C lcd2(LCD2, 20, 4);
LiquidCrystal_I2C lcd3(LCD3, 16, 2); 

// data storage to read string from serial port, 
// i.e. read function gets by 1 byte, thus int incomingByte is enough
int incomingByte;

// TIMER-REL Variables
unsigned long previousTime = 0;
const unsigned long timeoutDuration = 800; 

/*
 * TRANSACTION MODS-REL
 */
int8_t curMod = 0;
char MODS[][13] = { "BUY/OPEN   ", "SELL/OPEN   ", "CLOSE/CLOSE "};


/*
 * TRANSACTION-LOTS
 */
double MINLOT = 0.1;
double MAXLOT = 100;
double STEPLOT = 0.1;
double CURLOT = 0.1;

/*
 * USER-DEF STRUCTS
 */

struct KeyValue {
  String key;
  String value;
};

/*
 * USER-DEF FUNCS
 */

// Parse message received from Serial
struct KeyValue parseString(const String& data){ // expected String format is M[0-9]+:{VALUE}, i.e: M1:R; M3:BALANCE; ... 
  int colonPos = data.indexOf(':');

  String key = data.substring(0, colonPos);
  String value = data.substring(colonPos + 1);

  struct KeyValue storage = {key, value};
  return storage;
}

bool checkButton(int buttonPin){
  if(digitalRead(buttonPin) == HIGH)
  {
    delay(10);
    while(digitalRead(buttonPin) == HIGH);
    delay(10);
    return true;
  }
  return false;
}

void checkButtonsPressed(){
     if(checkButton(PIN_BUTST))
     {
        Serial.write("STOCK ");
     }
     if(checkButton(PIN_BUTMOD))
     {
        curMod++;
        if(curMod == MAX_MODS)
        {
          curMod = 0;
        }
        displayMods();
        Serial.write(MODS[curMod]);
     }
     if(checkButton(PIN_BUTACT))
     {
        Serial.write("ACT ");
     } 
     if(checkButton(PIN_BUTORDER)){
        Serial.write("ORDER ");
     }
     if(checkButton(PIN_BUTINC)){
        CURLOT += STEPLOT;
        if(CURLOT > MAXLOT){
          CURLOT = MAXLOT;
        }
        displayLots();
        Serial.write("INCLOT ");
     }
     if(checkButton(PIN_BUTDEC)){
        CURLOT -= STEPLOT;
        if(CURLOT<MINLOT){
          CURLOT = MINLOT;
        }
        displayLots();
        Serial.write("DECLOT");
     }
}

String getFloatingFormat(){
  char str[20];
  sprintf(str, ".10f", CURLOT);
  int digits = strchr(str, '0') - strchr(str, '.')-1;
  return (String(int(CURLOT*pow(10,digits))) + "," + String(digits));
}

void lightUpLedBuzz(const String& LEDCOLOR)
{
  previousTime = millis();
  tone(PIN_BUZZ, 100, 100);
  if(LEDCOLOR=="R"){
    digitalWrite(RED_LED, HIGH);
  }else if(LEDCOLOR == "G"){
    digitalWrite(GREEN_LED, HIGH);
  }
}

void displayMods(){
  lcd2.setCursor(0,3);
  lcd2.print("MODE:");
  lcd2.print(MODS[curMod]);
}

void clearLcds(){
  lcd.clear();
  lcd2.clear();
  lcd3.clear();
}

void displayStock(const String& str){
  lcd.setCursor(0,0);
  lcd.print(str);
}

void displayChange(const String& str){
  lcd.setCursor(0,1);
  lcd.print(str);
}

void displayAccount(const String& str){
  lcd2.setCursor(0,0);
  lcd2.print(str);
}

void displayBalance(const String& str){
  lcd2.setCursor(0,1);
  lcd2.print(str);
}

void displayLots(){
  lcd3.setCursor(0,0);
  lcd3.print("LOT: ");
  lcd3.print(CURLOT);
}

void displayMargin(const String& str){
  lcd3.setCursor(0,1);
  lcd3.print("MAR: ");
  lcd3.print(str);
  lcd3.print("PLN");
}

void displayOrder(const String& str){
  lcd2.setCursor(0,2);
  lcd2.print("ORDER: ");
  lcd2.print(str);
}

void performAction(const struct KeyValue& data){
  if(data.key == "M1"){
    lightUpLedBuzz(data.value);
  }else if(data.key == "M2"){
    clearLcds();
    displayMods();
    displayLots();
  }else if(data.key == "M3"){
    displayStock(data.value);
  }else if(data.key == "M4"){
    displayChange(data.value);
  }else if(data.key == "M5"){
    displayAccount(data.value);
  }else if(data.key == "M6"){
    displayBalance(data.value);
  }else if(data.key == "M7"){
    MINLOT = data.value.toFloat();
  }else if(data.key == "M8"){
    MAXLOT = data.value.toFloat();
  }else if(data.key == "M9"){
    STEPLOT = data.value.toFloat();
  }else if(data.key == "M10"){
    // sync cur lots here
    CURLOT = data.value.toFloat();
  }else if(data.key == "M11"){
    displayMargin(data.value);    
  }else if(data.key == "M12"){
    displayOrder(data.value);
  }

}


void setup() {
  // Initialize all components
  lcd.init();
  lcd.backlight();
  lcd2.init();
  lcd2.backlight();
  lcd3.init();
  lcd3.backlight();
  lcd.setCursor(0,0);
  lcd.print("LOADING...");
  lcd2.setCursor(0,0);
  lcd2.print("LOADING...");
  lcd3.setCursor(0,0);
  lcd3.print("LOADING...");
  Serial.begin(BRATE);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(PIN_BUTST, INPUT);
  pinMode(PIN_BUTMOD, INPUT);
  pinMode(PIN_BUZZ, OUTPUT);
}

void loop(){
  /*
   * CURRENT TIME
   */
  unsigned long currentTime = millis();
       // BUTTONS CHECK
    checkButtonsPressed();
  /*
   * POLLING FOR SERIAL (not effective)
   */
  while(Serial.available() > 0)
  {
    
    // BUFFER and BUFFER POS
    static char msg[MAX_MSG_LGT];
    static unsigned int msg_pos = 0;
    incomingByte = Serial.read();
    if(incomingByte != ';' && (msg_pos < MAX_MSG_LGT - 1))
    {
      // Add the incoming byte to message
      msg[msg_pos] = incomingByte;
      msg_pos++;   
    }
    // FULL M[0-9]+ received
    else{
      msg[msg_pos] = '\0';
      msg_pos = 0;
      struct KeyValue parsedData = parseString(msg);
      performAction(parsedData);
      
    }
  }
    // ACTIONS AFTER TIMEOUT IF WAS LAUNCHED
    if(currentTime - previousTime >= timeoutDuration)
    {
      noTone(PIN_BUZZ);
      digitalWrite(GREEN_LED, LOW);
      digitalWrite(RED_LED, LOW);
      previousTime = currentTime;
    }
}
