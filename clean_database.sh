#!/bin/bash
echo "Begin cleaning up the database..."

records_to_delete=()
while read apk_id package_name date_published
do
	file_exists=false
	for file in /conflux/Android/*.apk; do
		if [ $file == "/conflux/Android/${package_name}-${date_published.apk}" ]; then
			file_exists=true
			break
		fi
	done

	if [ "$file_exists" == false ]; then
		echo "Respective file for apk_id = ${apk_id} does not exist"
		records_to_delete=(${records_to_delete[@]} apk_id)
	fi
done < <(mysql --user=AppDataDBUser --password=7Rk5qx5k5AT7B0bNQD843pWNuADkKt4jQSnyAI8DNpjjgLlUamlGAgtMrzzK0Xu AppDataDB --execute="SELECT apk_id, package_name, date_published FROM apk_information")

for apk_id in ${records_to_delete[@]}; do
	echo "Removing record apk_id = ${apk_id} from database"
	# mysql --user=AppDataDBUser --password=7Rk5qx5k5AT7B0bNQD843pWNuADkKt4jQSnyAI8DNpjjgLlUamlGAgtMrzzK0Xu AppDataDB --execute="DELETE FROM apk_information WHERE apk_id='$apk_id'"
done

echo "Database cleanup complete!"
