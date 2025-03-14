#include "stm32f10x.h"                  // Device header
#include "Delay.h"
#include "OLED.h"
#include "Serial.h"
#include "LED.h"
uint8_t RxData;			//定义用于接收串口数据的变量

int main(void)
{
	/*模块初始化*/
	OLED_Init();		//OLED初始化
	
	/*显示静态字符串*/
	OLED_ShowString(1, 1, "RxData:");
	uint8_t pinState = GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_0); // 读取PA0电平[3,6](@ref)'
	OLED_ShowNum(1, 10, pinState,2);
	/*串口初始化*/
	Serial_Init();		//串口初始化
	LED_Init();
	while (1)
	{
		if (Serial_GetRxFlag() == 1)			//检查串口接收数据的标志位
		{
			RxData = Serial_GetRxData();		//获取串口接收的数据
			Serial_SendByte(RxData);			//串口将收到的数据回传回去，用于测试
			if(RxData==0){
				LED1_ON();
			}
			if(RxData==1){
				LED1_OFF();
			}
			OLED_ShowHexNum(1, 8, RxData, 2);	//显示串口接收的数据
		}
	}
}
