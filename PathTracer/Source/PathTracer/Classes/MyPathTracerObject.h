// Copyright 1998-2015 Epic Games, Inc. All Rights Reserved.

#pragma once

#include "MyPathTracerObject.generated.h"


/**
 * Example UStruct declared in a plugin module
 */
USTRUCT()
struct FMyPathTracerStruct
{
	GENERATED_USTRUCT_BODY()
 
	UPROPERTY()
	FString TestString;
};
 

/**
 * Example of declaring a UObject in a plugin module
 */
UCLASS()
class UMyPathTracerObject : public UObject
{
	GENERATED_BODY()

public:
	UMyPathTracerObject(const FObjectInitializer& ObjectInitializer);

private:

	UPROPERTY()
	FMyPathTracerStruct MyStruct;

};


