# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-26 AS build
ARG MODULE
WORKDIR /src
COPY docker/maven-settings.xml /tmp/settings.xml
COPY app/restful-booker-platform/${MODULE}/ ./
RUN --mount=type=cache,target=/root/.m2/repository \
    mvn -B -s /tmp/settings.xml -DskipTests package

FROM eclipse-temurin:26-jre-alpine
ARG MODULE
WORKDIR /app
COPY --from=build /src/target/restful-booker-platform-${MODULE}-*-exec.jar ./app.jar

ENV authDomain=rbp-auth
ENV bookingDomain=rbp-booking
ENV messageDomain=rbp-message
ENV roomDomain=rbp-room
ENV profile=prod
ENV JAVA_OPTS="-Xms128m -Xmx384m -XX:MaxMetaspaceSize=96m -XX:+UseContainerSupport"

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar -Dspring.profiles.active=$profile -Dhoneycomb.beeline.write-key=${HONEYCOMB_API_KEY} ./app.jar"]
